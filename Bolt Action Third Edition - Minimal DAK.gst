<?xml version="1.0" encoding="UTF-8"?>
<gameSystem xmlns="http://www.battlescribe.net/schema/gameSystemSchema"
            id="1f7d-0c61-7e6a-4cc6"
            name="Bolt Action 3ed"
            battleScribeVersion="2.03"
            revision="21"
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
</gameSystem>
