<?xml version="1.0" encoding="UTF-8"?>
<gameSystem xmlns="http://www.battlescribe.net/schema/gameSystemSchema"
            id="1f7d-0c61-7e6a-4cc6"
            name="Bolt Action 3ed"
            battleScribeVersion="2.03"
            revision="10"
            type="gameSystem"
            authorName="Jasseji / ChatGPT"
            authorUrl="https://github.com/Jasseji/bolt-action-3e-data">
  <costTypes>
    <costType name="Points" id="d4a9-f78c-67cc-4b69" defaultCostLimit="-1" hidden="false"/>
  </costTypes>
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
  </categoryEntries>
  <forceEntries>
    <forceEntry name="Rifle Platoon" id="c450-b14b-a141-436f" hidden="false">
      <categoryLinks>
        <categoryLink name="Command" hidden="false" id="9000-0000-0000-0001" targetId="2b35-7c65-b12a-4aca" type="category">
          <constraints>
            <constraint type="max" value="1" field="selections" scope="parent" shared="true" id="9200-0000-0000-0001"/>
          </constraints>
        </categoryLink>
        <categoryLink name="Infantry" hidden="false" id="9000-0000-0000-0002" targetId="d42d-87f6-d04b-43db" type="category">
          <constraints>
            <constraint type="max" value="5" field="selections" scope="parent" shared="true" id="9200-0000-0000-0002"/>
          </constraints>
        </categoryLink>
        <categoryLink name="Support" hidden="false" id="9000-0000-0000-0003" targetId="bcf5-f270-8171-47b4" type="category">
          <constraints>
            <constraint type="max" value="5" field="selections" scope="parent" shared="true" id="9200-0000-0000-0003"/>
          </constraints>
        </categoryLink>
        <categoryLink name="Transport" hidden="false" id="9000-0000-0000-0009" targetId="7a12-835d-246f-48a3" type="category"><constraints><constraint type="max" value="6" field="selections" scope="parent" shared="true" id="9200-0000-0000-0009"/></constraints></categoryLink>
      </categoryLinks>
    </forceEntry>
    <forceEntry name="Heavy Weapons Platoon" id="69c3-4cff-d235-4995" hidden="false">
      <categoryLinks>
        <categoryLink name="Command" hidden="false" id="9000-0000-0000-0004" targetId="2b35-7c65-b12a-4aca" type="category">
          <constraints>
            <constraint type="max" value="1" field="selections" scope="parent" shared="true" id="9200-0000-0000-0004"/>
          </constraints>
        </categoryLink>
        <categoryLink name="Support" hidden="false" id="9000-0000-0000-0005" targetId="bcf5-f270-8171-47b4" type="category">
          <constraints>
            <constraint type="max" value="6" field="selections" scope="parent" shared="true" id="9200-0000-0000-0005"/>
          </constraints>
        </categoryLink>
      </categoryLinks>
    </forceEntry>
    <forceEntry name="Artillery Platoon" id="fb70-3c83-743c-4b43" hidden="false">
      <categoryLinks>
        <categoryLink name="Command" hidden="false" id="9000-0000-0000-0006" targetId="2b35-7c65-b12a-4aca" type="category">
          <constraints>
            <constraint type="max" value="1" field="selections" scope="parent" shared="true" id="9200-0000-0000-0006"/>
          </constraints>
        </categoryLink>
        <categoryLink name="Artillery" hidden="false" id="9000-0000-0000-0007" targetId="3c3f-de12-7949-45f5" type="category">
          <constraints>
            <constraint type="max" value="4" field="selections" scope="parent" shared="true" id="9200-0000-0000-0007"/>
          </constraints>
        </categoryLink>
        <categoryLink name="Transport" hidden="false" id="9000-0000-0000-0010" targetId="7a12-835d-246f-48a3" type="category"><constraints><constraint type="max" value="4" field="selections" scope="parent" shared="true" id="9200-0000-0000-0010"/></constraints></categoryLink>
      </categoryLinks>
    </forceEntry>
    <forceEntry name="Armoured Platoon" id="bf40-789b-9656-4427" hidden="false">
      <categoryLinks>
        <categoryLink name="Armour" hidden="false" id="9000-0000-0000-0008" targetId="6912-835d-246f-48a2" type="category">
          <constraints>
            <constraint type="max" value="5" field="selections" scope="parent" shared="true" id="9200-0000-0000-0008"/>
          </constraints>
        </categoryLink>
      </categoryLinks>
    </forceEntry>
  </forceEntries>
</gameSystem>
