# Bolt Action 3ed – Armies of Germany

Poprawka błędu ładowania Army Book w NewRecruit.

Najważniejsza zmiana:
- poprawiono `selectionEntryLinks` na prawidłowe `entryLinks`;
- podniesiono revision systemu i katalogu do 2;
- uproszczono strukturę do działającego przykładu NewRecruit;
- dodano kategorie i ograniczenia plutonów.

## Aktualizacja
Usuń lub zastąp w repozytorium stare pliki `.gst` i `.cat` tymi z paczki.
Plików `.ros` i `.rosz` na razie nie wrzucaj — najpierw testujemy tworzenie pustej listy.

## Konfiguracja jednostek

- jednostkę dodaje się do odpowiedniego plutonu, a doświadczenie i wyposażenie wybiera się wewnątrz jej wpisu;
- dwa gotowe warianty Heer Infantry Squad zastąpiono jednym konfigurowalnym oddziałem;
- Heer Infantry Squad używa bezpośredniej grupy `Squad Members` 5–10 jak dane 2E: obowiązkowy NCO, 4–9 riflemenów i wymagany wybór Rifle/SMG wewnątrz NCO;
- opcja LMG automatycznie zastępuje dwóch bazowych riflemenów wpisami `LMG Gunner` i `LMG Loader with rifle`, bez zmiany całkowitej liczebności oddziału;
- skład drużyny jest prezentowany jako modele: NCO, aktualna liczba riflemenów oraz - po wybraniu - gunner i loader LMG;
- modele składu mają przypisaną broń, aby NewRecruit zawsze wyświetlał Riflemenów, LMG Gunnera i Loadera w punktowanym podsumowaniu jednostki;
- okres jednostki nie jest dopisywany do jej nazwy; jest widoczny w profilu przez techniczne kategorie zgodne z army bookiem;
- NCO i Riflemani mają Rifle ustawiony jako wybór domyślny, a opcja LMG Team jest uporządkowana na końcu listy opcji;
- Panzer III Ausf. L/M i Ausf. N są dostępne wyłącznie jako Regular lub Veteran, zgodnie z Armies of Germany: Third Edition;
- stare wpisy pozostają ukryte, aby wcześniejsze roster files nadal mogły je rozwiązać.
