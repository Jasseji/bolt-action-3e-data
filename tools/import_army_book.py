"""Import unit cards from Armies of Germany: Third Edition into the catalogue.

The PDF has a regular card layout.  This importer extracts the labelled fields,
keeps their wording in an Army Book profile, and turns experience prices and
option bullets into New Recruit selections.  Existing hand-authored entries are
left untouched.
"""

from __future__ import annotations

import argparse
import copy
import difflib
import hashlib
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


NS = "http://www.battlescribe.net/schema/catalogueSchema"
ET.register_namespace("", NS)

PROFILE_TYPE = "9b00-0000-0000-0001"
PROFILE_FIELDS = {
    "Period": "9b01-0000-0000-0001",
    "Composition / Type": "9b01-0000-0000-0002",
    "Weapons": "9b01-0000-0000-0003",
    "Rules and options": "9b01-0000-0000-0004",
    "Army Book": "9b01-0000-0000-0005",
}
WEAPON_PROFILE_TYPE = "9b00-0000-0000-0002"
WEAPON_FIELDS = {
    "Range": "9b02-0000-0000-0001", "Shots": "9b02-0000-0000-0002",
    "Pen": "9b02-0000-0000-0003", "Special Rules": "9b02-0000-0000-0004",
}
POINTS = "d4a9-f78c-67cc-4b69"
RULE_IDS = {
    "Hitler's Buzz-Saw": "a300-0000-0000-0001",
    "Blitzkrieg": "a300-0000-0000-0002",
    "Initiative Training": "a300-0000-0000-0003",
    "Panzer Ace": "a300-0000-0000-0004",
    "Defend the Fatherland!": "a300-0000-0000-0005",
    "Schurzen Armoured Skirts": "a300-0000-0000-0009",
    "Demolition Charges": "a300-0000-0000-0010",
}

CATEGORIES = {
    "Command": "2b35-7c65-b12a-4aca",
    "Infantry": "d42d-87f6-d04b-43db",
    "Support": "bcf5-f270-8171-47b4",
    "Artillery": "3c3f-de12-7949-45f5",
    "Armour": "6912-835d-246f-48a2",
    "Transport": "7a12-835d-246f-48a3",
}
PERIOD_CATEGORIES = {
    "E": "9e10-0000-0000-0001",
    "M": "9e10-0000-0000-0002",
    "L": "9e10-0000-0000-0003",
}
PLATOONS = {
    "Command": ("Rifle Platoon", "9d10-0000-0000-0001"),
    "Infantry": ("Rifle Platoon", "9d10-0000-0000-0001"),
    "Support": ("Heavy Weapons Platoon", "9d10-0000-0000-0002"),
    "Artillery": ("Artillery Platoon", "9d10-0000-0000-0003"),
    "Armour": ("Armoured Platoon", "9d10-0000-0000-0004"),
    "Transport": ("Armoured Platoon", "9d10-0000-0000-0004"),
}

SECTION_HEADINGS = {
    "BOLT ACTION", "INFANTRY", "HEADQUARTERS UNITS",
    "INFANTRY SQUADS AND TEAMS", "ARTILLERY", "FIELD ARTILLERY",
    "RECOILLESS ARTILLERY", "ANTI-AIRCRAFT GUNS", "ANTI-TANK GUNS",
    "VEHICLES", "TAN KS", "TANKS", "T ANKS",
    "TANK DESTROYERS AND ASSAULT GUNS",
    "T ANK DESTROYERS AND ASSAUL T GUNS",
    "SELF-PROPELLED ARTILLERY", "ANTI-AIRCRAFT VEHICLES",
    "ARMOURED CARS", "TRANSPORTS AND TOWS", "AMBULANCES",
    "CAPTURED AND REPURPOSED VEHICLES",
}
FALSE_HEADINGS = {
    "MMG", "6,000.", "90.", "WITH 76.2MM PAK 36(R)",
}
GUIDE_PAGES = {"E": (118, 119), "M": (121, 122, 123), "L": (125, 126)}
SUPPORT_WORDS = (
    "MACHINE GUN TEAM", "PANZERSCHRECK", "ANTI-TANK RIFLE TEAM",
    "FLAMETHROWER TEAM", "GOLIATH", "MORTAR TEAM", "SNIPER TEAM",
)


@dataclass
class Card:
    name: str
    page: int
    category: str
    period: str
    cost: str
    composition: str
    weapons: str
    damage: str
    options: list[str]
    rules: list[str]


def q(name: str) -> str:
    return f"{{{NS}}}{name}"


def stable_id(kind: str, value: str) -> str:
    raw = hashlib.sha1(f"aog3:{kind}:{value}".encode("utf-8")).hexdigest()[:16]
    return "-".join(raw[i : i + 4] for i in range(0, 16, 4))


def clean(text: str) -> str:
    text = text.replace("\u00ad", "").replace("–", "-").replace("—", "-")
    text = re.sub(r"(?<=\w)-\s*\n\s*(?=\w)", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" -\n\t")


def heading_key(text: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "", text.upper())


def candidate_headings(page_text: str) -> list[tuple[int, str]]:
    lines = list(re.finditer(r"(?m)^(.+?)\s*$", page_text))
    found: list[tuple[int, str]] = []
    for index, match in enumerate(lines):
        name = clean(match.group(1))
        if not name or name.upper() != name or len(name) < 4 or len(name) > 90:
            continue
        if name in SECTION_HEADINGS or name in FALSE_HEADINGS or name.startswith("THE ARMY LIST"):
            continue
        following = page_text[match.end() : match.end() + 5000]
        next_upper = None
        for later in lines[index + 1 :]:
            later_name = clean(later.group(1))
            if (
                later_name.upper() == later_name
                and later_name not in SECTION_HEADINGS
                and later_name not in FALSE_HEADINGS
            ):
                next_upper = later.start()
                break
        cost_pos = following.find("Cost")
        if cost_pos < 0:
            continue
        if next_upper is not None and match.end() + cost_pos > next_upper:
            continue
        if re.search(r"\b(Cost|Composition|Weapons|Options|Special Rules|damage Value)\b", name):
            continue
        found.append((match.start(), name))
    return found


def field(block: str, label: str, next_labels: tuple[str, ...]) -> str:
    block = re.sub(r"\s+", " ", block)
    stops = "|".join(re.escape(item) for item in next_labels)
    match = re.search(rf"(?is)\b{re.escape(label)}\b\s*(.*?)(?=\b(?:{stops})\b|$)", block)
    return clean(match.group(1)) if match else ""


def bullets(text: str) -> list[str]:
    if not text:
        return []
    parts = re.split(r"\s+-\s+(?=[A-Z0-9])|^-\s*", " " + text, flags=re.MULTILINE)
    return [clean(item) for item in parts if clean(item)]


def category_for(page: int, name: str) -> str:
    if page <= 28 and name in {"OFFICER", "MEDIC", "CHAPLAIN", "FORWARD OBSERVER"}:
        return "Command"
    if page <= 49:
        return "Support" if any(word in name for word in SUPPORT_WORDS) else "Infantry"
    if page <= 55:
        return "Artillery"
    if 86 <= page <= 93 or page == 103:
        return "Transport"
    return "Armour"


def display_name(name: str) -> str:
    name = clean(name).title()
    fixes = {
        "Assaul T": "Assault", "Renaul T": "Renault", "Maul Tier": "Maultier",
        "Ausf .": "Ausf.", "Gep .": "Gep.", "Ss ": "SS ", "Roa ": "ROA ",
        "Rso ": "RSO ", "Bmw ": "BMW ", "Sg6": "SG6", "Lg40": "LG40",
        "Aa/At": "AA/AT", "Aa ": "AA ", "At ": "AT ", "Mm ": "MM ",
        "Pzkpw": "PzKpw", "Pzkpfw": "PzKpfw", "Stug": "StuG", "Stuh": "StuH",
        "Sig ": "sIG ", "Cm ": "cm ", " ]": "",
    }
    for old, new in fixes.items():
        name = name.replace(old, new)
    name = re.sub(r"\b(I|Ii|Iii|Iv|V|Vi|Vii|Viii)\b", lambda m: m.group(1).upper(), name)
    name = re.sub(r"\b(Sd\.Kfz|Kfz|Pak|Flak|MMG|LG)\b", lambda m: m.group(1), name, flags=re.I)
    return name.strip(" ]")


def periods_for_page(text: str, count: int) -> list[str]:
    periods = re.findall(r"Period\s+([EML](?:\s*/\s*[EML]){0,2})", text, re.I)
    periods = [re.sub(r"\s+", "", item.upper()) for item in periods]
    if len(periods) >= count:
        return periods[-count:]
    return periods + ["E/M/L"] * (count - len(periods))


def guide_items(reader: PdfReader) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for period, page_numbers in GUIDE_PAGES.items():
        text = "\n".join(reader.pages[page].extract_text() or "" for page in page_numbers)
        chunks = re.findall(
            r"(?ms)^•\s*(.*?)(?=^•\s*|^[A-Z][A-Z &\-]{4,}\s*$|^\*\*\s*=|\Z)", text
        )
        result[period] = [clean(chunk.replace("**", "")) for chunk in chunks if clean(chunk)]
    return result


def guide_period(name: str, guides: dict[str, list[str]], fallback: str) -> str:
    key = heading_key(name)
    aliases = {
        "PANZERIIAUSFABCF": "PANZERII",
        "BRANDENBURGERSPECIALFORCESSQUAD": "BRANDENBURGERSSPECIALFORCESSQUAD",
        "TRUCKS": "TRUCK",
        "PANTHERTURM": "PATHERTURM",
    }
    compare_key = aliases.get(key, key)
    available: list[str] = []
    for period, items in guides.items():
        matched = False
        for item in items:
            item_key = heading_key(display_name(item))
            if compare_key == item_key:
                matched = True
                break
            if len(compare_key) >= 8 and item_key.startswith(compare_key):
                matched = True
                break
            ratio = difflib.SequenceMatcher(None, compare_key, item_key).ratio()
            if ratio >= 0.93:
                matched = True
                break
        if matched:
            available.append(period)
    return "/".join(available) if available else fallback


def extract_cards(pdf: Path) -> list[Card]:
    reader = PdfReader(str(pdf))
    guides = guide_items(reader)
    pages = {page: (reader.pages[page].extract_text() or "") for page in range(26, 104)}
    located: list[tuple[int, int, str]] = []
    for page, text in pages.items():
        located.extend((page, pos, name) for pos, name in candidate_headings(text))

    # These cards cross a page boundary or have unusually long introductory text.
    manual = {
        26: ["OFFICER"],
        36: ["BRANDENBURGER SPECIAL FORCES SQUAD"],
        45: ["FRENCH MILICE SQUAD"],
        64: ["STUG III AND VARIANTS, STUG IV"],
        60: ["PANZER 38(T) AND 35(T)"],
        72: ["BORGWARD B-IV DEMOLITION VEHICLE"],
        74: ["SD.KFZ 250/8 STUMMEL", "SD.KFZ 251/9 STUMMEL"],
        96: ["PANZER 35H 734(F) AND PANZER 38H 735(F)"],
    }
    for page, names in manual.items():
        upper = pages[page].upper()
        for name in names:
            key = heading_key(name)
            if any(p == page and heading_key(n) == key for p, _, n in located):
                continue
            # Fuzzy line matching tolerates extraction spaces such as ASSAUL T.
            pos = -1
            best = 0.0
            for match in re.finditer(r"(?m)^(.+?)\s*$", pages[page]):
                line = clean(match.group(1))
                score = difflib.SequenceMatcher(None, heading_key(line), key).ratio()
                if score > best:
                    best = score
                    pos = match.start()
            if best < 0.72:
                pos = -1
            if pos >= 0:
                located.append((page, pos, name))

    located.sort(key=lambda item: (item[0], item[1]))
    cards: list[Card] = []
    by_page: dict[int, list[tuple[int, str]]] = {}
    for page, pos, name in located:
        by_page.setdefault(page, []).append((pos, name))

    for page, entries in sorted(by_page.items()):
        page_periods = periods_for_page(pages[page], len(entries))
        for item_index, (pos, name) in enumerate(entries):
            if item_index + 1 < len(entries):
                block = pages[page][pos : entries[item_index + 1][0]]
            else:
                block = pages[page][pos:]
                if page + 1 in pages:
                    next_entries = by_page.get(page + 1, [])
                    continuation_end = next_entries[0][0] if next_entries else len(pages[page + 1])
                    block += "\n" + pages[page + 1][:continuation_end]

            cost = field(block, "Cost", ("Composition", "Weapons", "damage Value", "Options", "Special Rules", "Period"))
            if not cost:
                continue
            composition = field(block, "Composition", ("Weapons", "damage Value", "Options", "Special Rules", "Period"))
            weapons = field(block, "Weapons", ("damage Value", "Options", "Special Rules", "Period"))
            damage = field(block, "damage Value", ("Options", "Special Rules", "Period"))
            options_text = field(block, "Options", ("Special Rules", "Period"))
            rules_text = field(block, "Special Rules", ("Period",))
            card_name = display_name(name)
            extracted_period = page_periods[item_index] if item_index < len(page_periods) else "E/M/L"
            cards.append(
                Card(
                    name=card_name,
                    page=page,
                    category=category_for(page, name),
                    period=guide_period(card_name, guides, extracted_period),
                    cost=cost,
                    composition=composition,
                    weapons=weapons,
                    damage=damage,
                    options=bullets(options_text),
                    rules=bullets(rules_text),
                )
            )
    return cards


def add_cost(parent: ET.Element, value: int) -> None:
    costs = ET.SubElement(parent, q("costs"))
    ET.SubElement(costs, q("cost"), {"name": "Points", "typeId": POINTS, "value": str(value)})


def experience_prices(text: str) -> list[tuple[str, int]]:
    flat = clean(text).replace(",", "")
    found: list[tuple[int, str, int]] = []
    for match in re.finditer(
        r"(\d+)\s*pts?\s*\((Inexperienced|Regular|Veteran)(?:s|\s+infantry)?\)", flat, re.I
    ):
        found.append((match.start(), match.group(2).title(), int(match.group(1))))
    for match in re.finditer(
        r"\((Inexperienced|Regular|Veteran)(?:s|\s+infantry)?\)\s*(\d+)\s*pts?", flat, re.I
    ):
        found.append((match.start(), match.group(1).title(), int(match.group(2))))
    found.sort()
    result: list[tuple[str, int]] = []
    for _, name, value in found:
        if name not in {item[0] for item in result}:
            result.append((name, value))
    return result


def option_cost(text: str) -> int:
    plus = re.search(r"\+(\d+)\s*pts?", text, re.I)
    minus = re.search(r"-(\d+)\s*pts?", text, re.I)
    if plus:
        return int(plus.group(1))
    if minus:
        return -int(minus.group(1))
    return 0


def option_max(text: str) -> int:
    match = re.search(r"(?:up to|add)\s+(\d+)", text, re.I)
    if match:
        return int(match.group(1))
    if re.search(r"per\s+(?:figure|man)|anybody", text, re.I):
        return 10
    return 1


def option_quality_prices(text: str) -> list[tuple[str, int]]:
    flat = clean(text).replace(",", "")
    found: list[tuple[str, int]] = []
    for match in re.finditer(
        r"\+?(\d+)\s*pts?\s*\((Inexperienced|Regular|Veteran)(?:s)?\)", flat, re.I
    ):
        found.append((match.group(2).title(), int(match.group(1))))
    for match in re.finditer(
        r"\((Inexperienced|Regular|Veteran)(?:s)?\)\s*(?:at|for|or)?\s*\+?(\d+)\s*pts?", flat, re.I
    ):
        pair = (match.group(1).title(), int(match.group(2)))
        if pair not in found:
            found.append(pair)
    return found


def add_constraints(parent: ET.Element, maximum: int, seed: str) -> None:
    constraints = ET.SubElement(parent, q("constraints"))
    ET.SubElement(
        constraints,
        q("constraint"),
        {
            "type": "max", "value": str(maximum), "field": "selections",
            "scope": "parent", "shared": "false", "id": stable_id("constraint", seed),
        },
    )


def add_profile(entry: ET.Element, card: Card) -> None:
    profiles = ET.SubElement(entry, q("profiles"))
    profile = ET.SubElement(
        profiles,
        q("profile"),
        {
            "name": card.name, "hidden": "false", "id": stable_id("profile", card.name),
            "typeId": PROFILE_TYPE, "typeName": "Army Book Unit",
        },
    )
    characteristics = ET.SubElement(profile, q("characteristics"))
    rules_and_options = "; ".join(card.rules + card.options) or "-"
    values = {
        "Period": card.period,
        "Composition / Type": "; ".join(filter(None, [card.composition, card.damage])) or "-",
        "Weapons": card.weapons or "None",
        "Rules and options": rules_and_options,
        "Army Book": f"p. {card.page}",
    }
    for name, type_id in PROFILE_FIELDS.items():
        node = ET.SubElement(characteristics, q("characteristic"), {"name": name, "typeId": type_id})
        node.text = values[name]
    if "EW 141" in card.weapons:
        add_weapon_profile(profiles, card.name, "EW 141", '36"', "2", "+2", "Squeeze-bore, experimental")


def add_weapon_profile(
    profiles: ET.Element, seed: str, name: str, range_value: str,
    shots: str, pen: str, special: str,
) -> None:
    profile = ET.SubElement(
        profiles, q("profile"),
        {
            "name": name, "hidden": "false", "id": stable_id(f"weapon-{name}", seed),
            "typeId": WEAPON_PROFILE_TYPE, "typeName": "Weapon",
        },
    )
    characteristics = ET.SubElement(profile, q("characteristics"))
    values = {"Range": range_value, "Shots": shots, "Pen": pen, "Special Rules": special}
    for field_name, type_id in WEAPON_FIELDS.items():
        node = ET.SubElement(characteristics, q("characteristic"), {"name": field_name, "typeId": type_id})
        node.text = values[field_name]


def add_option_weapon_profiles(choice: ET.Element, card: Card, index: int, option: str) -> None:
    specs: list[tuple[str, str, str, str, str]] = []
    lower = option.lower()
    if "demolition charge" in lower:
        specs.append(("Demolition Charge", "-", "1", "HE", 'HE (3"), one-shot'))
    if "grb-39" in lower:
        specs.extend([
            ("GrB-39 (Anti-Personnel)", '24"', "1", "HE", 'HE (1")'),
            ("GrB-39 (Anti-Tank)", '24"', "1", "+3", "Shaped charge"),
        ])
    if "sturmpistole" in lower:
        specs.append(("Sturmpistole", '6"', "1", "+3", "Shaped charge"))
    if not specs:
        return
    profiles = ET.SubElement(choice, q("profiles"))
    for name, range_value, shots, pen, special in specs:
        add_weapon_profile(profiles, f"{card.name}-{index}", name, range_value, shots, pen, special)


def add_card(shared: ET.Element, entry_links: ET.Element, card: Card) -> None:
    entry_id = stable_id("unit", card.name)
    entry = ET.SubElement(
        shared, q("selectionEntry"),
        {"type": "unit", "import": "true", "name": card.name, "hidden": "false", "id": entry_id},
    )
    category_links = ET.SubElement(entry, q("categoryLinks"))
    ET.SubElement(
        category_links, q("categoryLink"),
        {
            "targetId": CATEGORIES[card.category], "id": stable_id("category", card.name),
            "primary": "true", "name": card.category,
        },
    )
    for period in re.findall(r"[EML]", card.period):
        ET.SubElement(
            category_links, q("categoryLink"),
            {
                "targetId": PERIOD_CATEGORIES[period],
                "id": stable_id(f"period-{period}", card.name),
                "primary": "false", "name": {"E": "Period: Early War", "M": "Period: Mid War", "L": "Period: Late War"}[period],
            },
        )
    searchable = " ".join(card.rules + card.options)
    applicable = ["Hitler's Buzz-Saw", "Initiative Training"]
    if card.name == "Officer":
        applicable.append("Blitzkrieg")
    if "Panzer Ace" in searchable:
        applicable.append("Panzer Ace")
    if "Defend the Fatherland" in searchable:
        applicable.append("Defend the Fatherland!")
    if "Schürzen" in searchable or "Schurzen" in searchable:
        applicable.append("Schurzen Armoured Skirts")
    if "demolition charge" in searchable.lower():
        applicable.append("Demolition Charges")
    info_links = ET.SubElement(entry, q("infoLinks"))
    for rule_name in applicable:
        ET.SubElement(
            info_links, q("infoLink"),
            {
                "name": rule_name, "hidden": "false", "type": "rule",
                "id": stable_id(f"rule-{rule_name}", card.name), "targetId": RULE_IDS[rule_name],
            },
        )
    add_profile(entry, card)

    groups = ET.SubElement(entry, q("selectionEntryGroups"))
    prices = experience_prices(card.cost)
    if prices:
        group = ET.SubElement(groups, q("selectionEntryGroup"), {"name": "Experience", "id": stable_id("experience", card.name)})
        constraints = ET.SubElement(group, q("constraints"))
        for kind in ("min", "max"):
            ET.SubElement(
                constraints, q("constraint"),
                {
                    "type": kind, "value": "1", "field": "selections", "scope": "parent",
                    "shared": "false", "id": stable_id(f"experience-{kind}", card.name),
                },
            )
        selections = ET.SubElement(group, q("selectionEntries"))
        for quality, points in prices:
            choice = ET.SubElement(
                selections, q("selectionEntry"),
                {"type": "upgrade", "name": quality, "id": stable_id(f"quality-{quality}", card.name)},
            )
            add_cost(choice, points)
    else:
        plain = re.search(r"(\d+)\s*pts?", card.cost.replace(",", ""), re.I)
        add_cost(entry, int(plain.group(1)) if plain else 0)

    if card.options:
        group = ET.SubElement(groups, q("selectionEntryGroup"), {"name": "Options", "id": stable_id("options", card.name)})
        selections = ET.SubElement(group, q("selectionEntries"))
        for index, option in enumerate(card.options, 1):
            choice = ET.SubElement(
                selections, q("selectionEntry"),
                {"type": "upgrade", "name": option, "id": stable_id(f"option-{index}", card.name)},
            )
            quality_prices = option_quality_prices(option)
            if quality_prices:
                modifiers = ET.SubElement(choice, q("modifiers"))
                for quality, points in quality_prices:
                    modifier = ET.SubElement(
                        modifiers, q("modifier"),
                        {"type": "set", "field": POINTS, "value": str(points)},
                    )
                    conditions = ET.SubElement(modifier, q("conditions"))
                    ET.SubElement(
                        conditions, q("condition"),
                        {
                            "field": "selections", "scope": entry_id, "value": "0",
                            "percentValue": "false", "shared": "true",
                            "includeChildSelections": "true", "includeChildForces": "false",
                            "childId": stable_id(f"quality-{quality}", card.name), "type": "greaterThan",
                        },
                    )
            add_constraints(choice, option_max(option), f"option-{index}-{card.name}")
            add_option_weapon_profiles(choice, card, index, option)
            add_cost(choice, quality_prices[0][1] if quality_prices else option_cost(option))

    if not prices and entry.find(q("costs")) is None:
        add_cost(entry, 0)
    elif prices:
        add_cost(entry, 0)

    platoon_name, platoon_id = PLATOONS[card.category]
    link = ET.SubElement(
        entry_links, q("entryLink"),
        {
            "import": "true", "name": card.name, "hidden": "false",
            "id": stable_id("entry-link", card.name), "type": "selectionEntry", "targetId": entry_id,
        },
    )
    links = ET.SubElement(link, q("categoryLinks"))
    ET.SubElement(
        links, q("categoryLink"),
        {
            "id": stable_id("platoon-link", card.name), "name": platoon_name,
            "hidden": "false", "targetId": platoon_id, "primary": "true",
        },
    )


def vehicle_variant_family(name: str) -> str | None:
    """Return the common vehicle name for entries split by Ausf. variants."""
    match = re.match(r"^(.+?)\s+Ausf\.?\s*.+$", name, re.I)
    return clean(match.group(1)) if match else None


def vehicle_variant_letters(name: str) -> set[str]:
    """Return the leading Ausf. letter set, used to discard strict duplicates."""
    match = re.search(r"\bAusf\.?\s*((?:[A-Z]\s*,?\s*)+)", name)
    if not match:
        return set()
    return set(re.findall(r"[A-Z]", match.group(1)))


def flatten_vehicle_families(
    shared: ET.Element, entry_links: ET.Element, generated_ids: set[str],
) -> None:
    """Restore hand-authored variants before a repeated import/regroup pass."""
    for root in list(shared.findall(q("selectionEntry"))):
        family = root.get("name", "")
        groups = root.find(q("selectionEntryGroups"))
        if groups is None:
            continue
        variant_group = None
        for group in groups.findall(q("selectionEntryGroup")):
            choices = group.find(q("selectionEntries"))
            if choices is None:
                continue
            names = [entry.get("name", "") for entry in choices.findall(q("selectionEntry"))]
            if group.get("id") == stable_id("vehicle-family-variants", family) or any(
                re.match(r"^Ausf(?:\.|\b)", name, re.I) for name in names
            ):
                variant_group = group
                break
        if variant_group is None:
            continue
        variants = variant_group.find(q("selectionEntries"))
        root_categories = root.find(q("categoryLinks"))
        if variants is not None:
            for variant in list(variants.findall(q("selectionEntry"))):
                if variant.get("id") in generated_ids:
                    continue
                variant_name = variant.get("name", "")
                if re.match(r"^Ausf(?:\.|\b)", variant_name, re.I):
                    variant.set("name", f"{family} {variant_name}")
                variant.set("type", "unit")
                variant.set("import", "true")
                category_links = variant.find(q("categoryLinks"))
                if category_links is None:
                    category_links = ET.Element(q("categoryLinks"))
                    variant.insert(0, category_links)
                existing_targets = {
                    link.get("targetId") for link in category_links.findall(q("categoryLink"))
                }
                if root_categories is not None:
                    for root_link in root_categories.findall(q("categoryLink")):
                        if root_link.get("targetId") in existing_targets:
                            continue
                        restored = copy.deepcopy(root_link)
                        restored.set(
                            "id",
                            stable_id(
                                f"restored-category-{root_link.get('targetId', '')}",
                                variant.get("name", ""),
                            ),
                        )
                        category_links.append(restored)
                shared.append(variant)
        shared.remove(root)
        for link in list(entry_links.findall(q("entryLink"))):
            if link.get("targetId") == root.get("id"):
                entry_links.remove(link)


def restore_orphaned_variant_names(shared: ET.Element) -> None:
    """Repair shortened top-level names left by older grouping passes."""
    for entry in shared.findall(q("selectionEntry")):
        if entry.get("type") != "unit" or not re.match(r"^Ausf(?:\.|\b)", entry.get("name", ""), re.I):
            continue
        profile = entry.find(f"{q('profiles')}/{q('profile')}")
        if profile is not None and vehicle_variant_family(profile.get("name", "")):
            entry.set("name", profile.get("name", ""))


def remove_superseded_vehicle_variants(entries: list[ET.Element]) -> list[ET.Element]:
    """Prefer a combined Army Book card over an older strict-subset variant."""
    keep: list[ET.Element] = []
    letter_sets = {entry.get("id", ""): vehicle_variant_letters(entry.get("name", "")) for entry in entries}
    for entry in entries:
        letters = letter_sets[entry.get("id", "")]
        strict_subset = bool(letters) and any(
            letters < other_letters
            for other in entries
            if other is not entry
            for other_letters in [letter_sets[other.get("id", "")]]
            if other_letters
        )
        same_variant = [
            other for other in entries
            if other is not entry and letters and letter_sets[other.get("id", "")] == letters
        ]
        entry_score = (
            entry.get("id") == stable_id("unit", entry.get("name", "")),
            entry.find(q("profiles")) is not None,
        )
        duplicate = any(
            (
                other.get("id") == stable_id("unit", other.get("name", "")),
                other.find(q("profiles")) is not None,
            ) > entry_score
            or (
                (
                    other.get("id") == stable_id("unit", other.get("name", "")),
                    other.find(q("profiles")) is not None,
                ) == entry_score
                and other.get("id", "") < entry.get("id", "")
            )
            for other in same_variant
        )
        if not strict_subset and not duplicate:
            keep.append(entry)
    return keep


def group_vehicle_variants(shared: ET.Element, entry_links: ET.Element) -> tuple[int, int]:
    """Replace multiple top-level Ausf. cards with one family and a required variant choice."""
    families: dict[str, list[ET.Element]] = {}
    for entry in shared.findall(q("selectionEntry")):
        if entry.get("type") != "unit":
            continue
        family = vehicle_variant_family(entry.get("name", ""))
        if family:
            families.setdefault(family, []).append(entry)

    grouped = 0
    removed = 0
    for family, all_variants in families.items():
        if len(all_variants) < 2:
            continue
        variants = remove_superseded_vehicle_variants(all_variants)
        removed += len(all_variants) - len(variants)
        first_index = min(list(shared).index(entry) for entry in all_variants)

        primary_links: list[ET.Element] = []
        for variant in variants:
            category_links = variant.find(q("categoryLinks"))
            if category_links is not None:
                primary_links.extend(
                    link for link in category_links.findall(q("categoryLink"))
                    if link.get("primary") == "true"
                )
        primary_targets = {link.get("targetId") for link in primary_links}
        if len(primary_targets) != 1:
            raise RuntimeError(f"Vehicle family {family!r} spans multiple primary categories")
        primary = copy.deepcopy(primary_links[0])
        primary.set("id", stable_id("vehicle-family-category", family))

        for variant in all_variants:
            shared.remove(variant)
            for link in list(entry_links.findall(q("entryLink"))):
                if link.get("targetId") == variant.get("id"):
                    entry_links.remove(link)

        root_id = stable_id("vehicle-family", family)
        root = ET.Element(
            q("selectionEntry"),
            {"type": "unit", "import": "true", "name": family, "hidden": "false", "id": root_id},
        )
        root_categories = ET.SubElement(root, q("categoryLinks"))
        root_categories.append(primary)
        groups = ET.SubElement(root, q("selectionEntryGroups"))
        group = ET.SubElement(
            groups, q("selectionEntryGroup"),
            {"name": "Vehicle variant (Ausf.)", "id": stable_id("vehicle-family-variants", family)},
        )
        constraints = ET.SubElement(group, q("constraints"))
        for kind in ("min", "max"):
            ET.SubElement(
                constraints, q("constraint"),
                {
                    "type": kind, "value": "1", "field": "selections", "scope": "parent",
                    "shared": "false", "id": stable_id(f"vehicle-family-variants-{kind}", family),
                },
            )
        choices = ET.SubElement(group, q("selectionEntries"))
        for variant in variants:
            variant.set("type", "upgrade")
            variant.attrib.pop("import", None)
            variant.set("name", variant.get("name", "")[len(family):].strip())
            category_links = variant.find(q("categoryLinks"))
            if category_links is not None:
                for link in list(category_links.findall(q("categoryLink"))):
                    if link.get("primary") == "true":
                        category_links.remove(link)
            choices.append(variant)
        add_cost(root, 0)
        shared.insert(first_index, root)

        category_name = primary.get("name", "")
        platoon_name, platoon_id = PLATOONS[category_name]
        link = ET.SubElement(
            entry_links, q("entryLink"),
            {
                "import": "true", "name": family, "hidden": "false",
                "id": stable_id("vehicle-family-entry-link", family),
                "type": "selectionEntry", "targetId": root_id,
            },
        )
        links = ET.SubElement(link, q("categoryLinks"))
        ET.SubElement(
            links, q("categoryLink"),
            {
                "id": stable_id("vehicle-family-platoon-link", family), "name": platoon_name,
                "hidden": "false", "targetId": platoon_id, "primary": "true",
            },
        )
        grouped += 1
    return grouped, removed


def import_cards(catalogue: Path, cards: list[Card]) -> tuple[int, int]:
    tree = ET.parse(catalogue)
    root = tree.getroot()
    shared = root.find(q("sharedSelectionEntries"))
    entry_links = root.find(q("entryLinks"))
    if shared is None or entry_links is None:
        raise RuntimeError("Catalogue lacks sharedSelectionEntries or entryLinks")

    generated_ids = {stable_id("unit", card.name) for card in cards}
    vehicle_variant_names = {
        heading_key(card.name) for card in cards if vehicle_variant_family(card.name)
    }
    flatten_vehicle_families(shared, entry_links, generated_ids)
    restore_orphaned_variant_names(shared)
    for node in list(shared.findall(q("selectionEntry"))):
        if (
            node.get("id") in generated_ids
            or heading_key(node.get("name", "")) in vehicle_variant_names
        ):
            shared.remove(node)
    for node in list(entry_links.findall(q("entryLink"))):
        if (
            node.get("targetId") in generated_ids
            or heading_key(node.get("name", "")) in vehicle_variant_names
        ):
            entry_links.remove(node)

    existing_names = {
        heading_key(node.get("name", ""))
        for node in shared.findall(q("selectionEntry"))
        if node.get("type") == "unit"
    }
    added = 0
    skipped = 0
    for card in cards:
        if heading_key(card.name) in existing_names:
            skipped += 1
            continue
        add_card(shared, entry_links, card)
        existing_names.add(heading_key(card.name))
        added += 1

    grouped, removed_variants = group_vehicle_variants(shared, entry_links)
    print(f"Grouped vehicle families: {grouped}; removed superseded variants: {removed_variants}")

    root.set("revision", str(int(root.get("revision", "0")) + 1))
    ET.indent(tree, space="  ")
    tree.write(catalogue, encoding="utf-8", xml_declaration=True)
    return added, skipped


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("catalogue", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    cards = extract_cards(args.pdf)
    print(f"Extracted cards: {len(cards)}")
    for card in cards:
        print(f"{card.page:03} | {card.category:9} | {card.period:5} | {card.name} | {card.cost[:55]}")
    if args.apply:
        added, skipped = import_cards(args.catalogue, cards)
        print(f"Added: {added}; skipped existing: {skipped}")


if __name__ == "__main__":
    main()
