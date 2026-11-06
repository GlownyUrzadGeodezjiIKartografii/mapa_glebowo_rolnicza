<?xml version="1.0" encoding="UTF-8"?>
<!-- Syntetyczny przyklad GML w schemacie MapaGlebowoRolnicza_2026 (namespace :3.0).
     Pokrywa: podloza "a" (4/4a, 3/3a) z rozna kolejnoscia w pliku, skalaMacierzysta
     wewnatrz opisPodloza, skala 4 i 5, szkieletowosc 3. Do weryfikacji recznej w QGIS. -->
<gml:FeatureCollection
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:gr="urn:gugik:specyfikacje:gmlas:mapaGlebowoRolnicza:3.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <gml:featureMember>
    <gr:GR_KonturGlebowy gml:id="PL.KONT.1">
      <gr:lokalnyId>PL.KONT.1</gr:lokalnyId>
      <gr:przestrzenNazw>MapaGlebowoRolnicza</gr:przestrzenNazw>
      <gr:wersjaObiektu>2026-01-01T00:00:00</gr:wersjaObiektu>
      <gr:poczatekWersjiObiektu>2026-01-01T00:00:00</gr:poczatekWersjiObiektu>
      <gr:dataUtworzenia>2026-01-01</gr:dataUtworzenia>
      <gr:teryt>1465011</gr:teryt>
      <gr:opisPodloza>
        <gr:numerPodloza>1</gr:numerPodloza>
        <gr:podloze>gl</gr:podloze>
      </gr:opisPodloza>
      <gr:opisPodloza>
        <gr:numerPodloza>4a</gr:numerPodloza>
        <gr:podloze>gs</gr:podloze>
        <gr:miazszosc>:</gr:miazszosc>
      </gr:opisPodloza>
      <gr:opisPodloza>
        <gr:numerPodloza>4</gr:numerPodloza>
        <gr:podloze>ps</gr:podloze>
        <gr:miazszosc>-</gr:miazszosc>
      </gr:opisPodloza>
      <gr:opisPodloza>
        <gr:numerPodloza>3a</gr:numerPodloza>
        <gr:podloze>gc</gr:podloze>
        <gr:miazszosc>:</gr:miazszosc>
      </gr:opisPodloza>
      <gr:opisPodloza>
        <gr:numerPodloza>3</gr:numerPodloza>
        <gr:podloze>gs</gr:podloze>
        <gr:miazszosc>-</gr:miazszosc>
      </gr:opisPodloza>
      <gr:skala>4</gr:skala>
      <gr:zrodlo>Teren</gr:zrodlo>
      <gr:geometria>
        <gml:Polygon gml:id="geom.PL.KONT.1" srsName="urn:ogc:def:crs:EPSG::2180">
          <gml:exterior>
            <gml:LinearRing>
              <gml:posList srsDimension="2">0 0 0 100 100 100 100 0 0 0</gml:posList>
            </gml:LinearRing>
          </gml:exterior>
        </gml:Polygon>
      </gr:geometria>
      <gr:aktualnosc>2026-01-01</gr:aktualnosc>
      <gr:kompleks>1</gr:kompleks>
      <gr:typPodtyp>A</gr:typPodtyp>
    </gr:GR_KonturGlebowy>
  </gml:featureMember>
  <gml:featureMember>
    <gr:GR_KonturGlebowy gml:id="PL.KONT.2">
      <gr:lokalnyId>PL.KONT.2</gr:lokalnyId>
      <gr:przestrzenNazw>MapaGlebowoRolnicza</gr:przestrzenNazw>
      <gr:wersjaObiektu>2026-01-01T00:00:00</gr:wersjaObiektu>
      <gr:poczatekWersjiObiektu>2026-01-01T00:00:00</gr:poczatekWersjiObiektu>
      <gr:dataUtworzenia>2026-01-01</gr:dataUtworzenia>
      <gr:teryt>1465011</gr:teryt>
      <gr:opisPodloza>
        <gr:numerPodloza>1</gr:numerPodloza>
        <gr:podloze>gs</gr:podloze>
        <gr:szkieletowosc>3</gr:szkieletowosc>
      </gr:opisPodloza>
      <gr:opisPodloza>
        <gr:numerPodloza>2</gr:numerPodloza>
        <gr:podloze>pl</gr:podloze>
        <gr:skalaMacierzysta>p</gr:skalaMacierzysta>
      </gr:opisPodloza>
      <gr:skala>5</gr:skala>
      <gr:zrodlo>Teren</gr:zrodlo>
      <gr:geometria>
        <gml:Polygon gml:id="geom.PL.KONT.2" srsName="urn:ogc:def:crs:EPSG::2180">
          <gml:exterior>
            <gml:LinearRing>
              <gml:posList srsDimension="2">200 200 200 300 300 300 300 200 200 200</gml:posList>
            </gml:LinearRing>
          </gml:exterior>
        </gml:Polygon>
      </gr:geometria>
      <gr:aktualnosc>2026-01-01</gr:aktualnosc>
      <gr:kompleks>2</gr:kompleks>
      <gr:typPodtyp>B</gr:typPodtyp>
    </gr:GR_KonturGlebowy>
  </gml:featureMember>
  <gml:featureMember>
    <!-- Ponad 5 opisow podloza (1,2,2a,3,3a,4,4a,5,5a) - test przypadku "liczba podloz > 5". -->
    <gr:GR_KonturGlebowy gml:id="PL.KONT.3">
      <gr:lokalnyId>PL.KONT.3</gr:lokalnyId>
      <gr:przestrzenNazw>MapaGlebowoRolnicza</gr:przestrzenNazw>
      <gr:wersjaObiektu>2026-01-01T00:00:00</gr:wersjaObiektu>
      <gr:poczatekWersjiObiektu>2026-01-01T00:00:00</gr:poczatekWersjiObiektu>
      <gr:dataUtworzenia>2026-01-01</gr:dataUtworzenia>
      <gr:teryt>1465011</gr:teryt>
      <gr:opisPodloza><gr:numerPodloza>1</gr:numerPodloza><gr:podloze>gl</gr:podloze></gr:opisPodloza>
      <gr:opisPodloza><gr:numerPodloza>2</gr:numerPodloza><gr:podloze>ps</gr:podloze><gr:miazszosc>-</gr:miazszosc></gr:opisPodloza>
      <gr:opisPodloza><gr:numerPodloza>2a</gr:numerPodloza><gr:podloze>gs</gr:podloze><gr:miazszosc>:</gr:miazszosc></gr:opisPodloza>
      <gr:opisPodloza><gr:numerPodloza>3</gr:numerPodloza><gr:podloze>pl</gr:podloze><gr:miazszosc>-</gr:miazszosc></gr:opisPodloza>
      <gr:opisPodloza><gr:numerPodloza>3a</gr:numerPodloza><gr:podloze>gc</gr:podloze><gr:miazszosc>:</gr:miazszosc></gr:opisPodloza>
      <gr:opisPodloza><gr:numerPodloza>4</gr:numerPodloza><gr:podloze>ps</gr:podloze><gr:miazszosc>-</gr:miazszosc></gr:opisPodloza>
      <gr:opisPodloza><gr:numerPodloza>4a</gr:numerPodloza><gr:podloze>gs</gr:podloze><gr:miazszosc>:</gr:miazszosc></gr:opisPodloza>
      <gr:opisPodloza><gr:numerPodloza>5</gr:numerPodloza><gr:podloze>gl</gr:podloze><gr:miazszosc>-</gr:miazszosc></gr:opisPodloza>
      <gr:opisPodloza><gr:numerPodloza>5a</gr:numerPodloza><gr:podloze>gs</gr:podloze><gr:miazszosc>:</gr:miazszosc></gr:opisPodloza>
      <gr:skala>1</gr:skala>
      <gr:zrodlo>Teren</gr:zrodlo>
      <gr:geometria>
        <gml:Polygon gml:id="geom.PL.KONT.3" srsName="urn:ogc:def:crs:EPSG::2180">
          <gml:exterior>
            <gml:LinearRing>
              <gml:posList srsDimension="2">400 400 400 500 500 500 500 400 400 400</gml:posList>
            </gml:LinearRing>
          </gml:exterior>
        </gml:Polygon>
      </gr:geometria>
      <gr:aktualnosc>2026-01-01</gr:aktualnosc>
      <gr:kompleks>3</gr:kompleks>
      <gr:typPodtyp>C</gr:typPodtyp>
    </gr:GR_KonturGlebowy>
  </gml:featureMember>
</gml:FeatureCollection>
