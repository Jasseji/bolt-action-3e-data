<?xml version="1.0" encoding="UTF-8"?>
<gameSystem xmlns="http://www.battlescribe.net/schema/gameSystemSchema"
            id="1f7d-0c61-7e6a-4cc6"
            name="Bolt Action 3ed"
            battleScribeVersion="2.03"
            revision="29"
            type="gameSystem"
            authorName="Jasseji / ChatGPT"
            authorUrl="https://github.com/Jasseji/bolt-action-3e-data">
  <costTypes>
    <costType name="Points" id="d4a9-f78c-67cc-4b69" defaultCostLimit="-1" hidden="false"/>
  </costTypes>
  <profileTypes>
    <profileType name="Army Book Unit" id="9b00-0000-0000-0001">
      <characteristicTypes>
        <characteristicType name="Period" id="9b01-0000-0000-0001"/>
        <characteristicType name="Composition / Type" id="9b01-0000-0000-0002"/>
        <characteristicType name="Weapons" id="9b01-0000-0000-0003"/>
        <characteristicType name="Rules and options" id="9b01-0000-0000-0004"/>
        <characteristicType name="Army Book" id="9b01-0000-0000-0005"/>
      </characteristicTypes>
    </profileType>
    <profileType name="Weapon" id="9b00-0000-0000-0002">
      <characteristicTypes>
        <characteristicType name="Range" id="9b02-0000-0000-0001"/>
        <characteristicType name="Shots" id="9b02-0000-0000-0002"/>
        <characteristicType name="Pen" id="9b02-0000-0000-0003"/>
        <characteristicType name="Special Rules" id="9b02-0000-0000-0004"/>
      </characteristicTypes>
    </profileType>
  </profileTypes>
  <categoryEntries>
    <categoryEntry name="Command" id="2b35-7c65-b12a-4aca" hidden="false"/>
    <categoryEntry name="Infantry" id="d42d-87f6-d04b-43db" hidden="false"/>
    <categoryEntry name="Support" id="bcf5-f270-8171-47b4" hidden="false"/>
    <categoryEntry name="Artillery" id="3c3f-de12-7949-45f5" hidden="false"/>
    <categoryEntry name="Armour" id="6912-835d-246f-48a2" hidden="false"/>
    <categoryEntry name="Transport" id="7a12-835d-246f-48a3" hidden="false"/>
    <categoryEntry name="Period: Early War" id="9e10-0000-0000-0001" hidden="false"/>
    <categoryEntry name="Period: Mid War" id="9e10-0000-0000-0002" hidden="false"/>
    <categoryEntry name="Period: Late War" id="9e10-0000-0000-0003" hidden="false"/>
    <categoryEntry name="Rifle Platoon" id="9d10-0000-0000-0001" hidden="false"/>
    <categoryEntry name="Heavy Weapons Platoon" id="9d10-0000-0000-0002" hidden="false"/>
    <categoryEntry name="Artillery Platoon" id="9d10-0000-0000-0003" hidden="false"/>
    <categoryEntry name="Armoured Platoon" id="9d10-0000-0000-0004" hidden="false"/>
  </categoryEntries>
  <forceEntries>
    <forceEntry name="Army List" id="c450-b14b-a141-436f" hidden="false">
      <categoryLinks>
        <categoryLink name="Rifle Platoon" hidden="false" id="9000-0000-0000-0101" targetId="9d10-0000-0000-0001" type="category"><constraints><constraint type="max" value="20" field="selections" scope="parent" shared="true" id="9200-0000-0000-0101"/></constraints></categoryLink>
        <categoryLink name="Heavy Weapons Platoon" hidden="false" id="9000-0000-0000-0102" targetId="9d10-0000-0000-0002" type="category"><constraints><constraint type="max" value="20" field="selections" scope="parent" shared="true" id="9200-0000-0000-0102"/></constraints></categoryLink>
        <categoryLink name="Artillery Platoon" hidden="false" id="9000-0000-0000-0103" targetId="9d10-0000-0000-0003" type="category"><constraints><constraint type="max" value="20" field="selections" scope="parent" shared="true" id="9200-0000-0000-0103"/></constraints></categoryLink>
        <categoryLink name="Armoured Platoon" hidden="false" id="9000-0000-0000-0104" targetId="9d10-0000-0000-0004" type="category"><constraints><constraint type="max" value="20" field="selections" scope="parent" shared="true" id="9200-0000-0000-0104"/></constraints></categoryLink>
      </categoryLinks>
    </forceEntry>
  </forceEntries>
  <sharedRules>
    <rule name="Hitler's Buzz-Saw" id="a300-0000-0000-0001" hidden="false"><description>German light and medium machine guns fire 1 extra shot. For vehicle-mounted weapons, first halve the number of shots rolled, then add 1.</description></rule>
    <rule name="Blitzkrieg" id="a300-0000-0000-0002" hidden="false"><description>Regular and Veteran German officers may take 1 additional order die from the bag when using You men, snap to action!</description></rule>
    <rule name="Initiative Training" id="a300-0000-0000-0003" hidden="false"><description>Regular and Veteran German units ignore the -1 morale penalty for losing their squad or team leader.</description></rule>
    <rule name="Panzer Ace" id="a300-0000-0000-0004" hidden="false"><description>One eligible Veteran vehicle in the force may be designated a Panzer Ace. Its main gun receives +1 Pen when rolling to damage enemy vehicles and +1 on vehicle damage tables. This does not apply to co-axial weapons.</description></rule>
    <rule name="Defend the Fatherland!" id="a300-0000-0000-0005" hidden="false"><description>Eligible infantry and artillery may be fielded as Fallschirmjager, Waffen-SS or Gebirgsjager and must apply the relevant quality upgrades, costs and rules.</description></rule>
    <rule name="Fallschirmjager" id="a300-0000-0000-0006" hidden="false"><description>The unit must be Veteran and must purchase Stubborn for +1 point per man.</description></rule>
    <rule name="Waffen-SS" id="a300-0000-0000-0007" hidden="false"><description>The unit must purchase Fanatics for +2 points per man. Inexperienced units additionally use the Mixed Quality rule described in Armies of Germany, page 23.</description></rule>
    <rule name="Gebirgsjager" id="a300-0000-0000-0008" hidden="false"><description>The unit must be Veteran and must purchase Fieldcraft for +1 point per man. It also receives Winter Equipment as described in Armies of Germany, page 23.</description></rule>
    <rule name="Schurzen Armoured Skirts" id="a300-0000-0000-0009" hidden="false"><description>Anti-tank rifles and shaped charges never receive the +1 penetration bonus for hitting a vehicle with Schurzen in the side.</description></rule>
    <rule name="Demolition Charges" id="a300-0000-0000-0010" hidden="false"><description>A demolition charge may be placed once per game with a Fire order and detonated after a subsequent Run move. It uses a 3-inch HE template and follows the detailed placement and detonation rules on page 25.</description></rule>
  </sharedRules>
</gameSystem>
