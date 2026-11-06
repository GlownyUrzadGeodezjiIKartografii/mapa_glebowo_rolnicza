# Lokalne schematy OGC (GML 3.2.1)

Ten katalog zawiera **lokalną kopię** zestawu schematów XSD dla GML 3.2.1 wraz z
pełnym łańcuchem zależności (OGC + W3C `xlink`/`xml`). Dzięki temu walidacja GML
nie wymaga dostępu do internetu i jest powtarzalna.

## Pochodzenie

- Punkt wejścia: `http://schemas.opengis.net/gml/3.2.1/gml.xsd`
- Zależności pobrane rekurencyjnie (import/include/redefine), 56 plików:
  - 54 z `schemas.opengis.net`
  - 2 z `www.w3.org`
- Struktura katalogów odwzorowuje hosta i ścieżkę źródłową:
  `ogc/<host>/<ścieżka>` (np. `ogc/schemas.opengis.net/gml/3.2.1/gml.xsd`).

## Jedyna modyfikacja względem oryginału

Atrybuty `schemaLocation` w elementach `import`/`include`/`redefine` zostały
przepisane na **lokalne ścieżki względne**, aby cały zestaw rozwiązywał się
offline (budowa z `no_network=True`). Treść merytoryczna schematów jest
nietknięta.

## Jak odtworzyć

Zestaw został pobrany skryptem crawlującym drzewo zależności od `gml.xsd`.
Aby zaktualizować, pobierz ponownie od tego samego punktu wejścia i powtórz
przepisanie `schemaLocation` na ścieżki względne.
