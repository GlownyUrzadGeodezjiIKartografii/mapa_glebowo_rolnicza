# Spec: obsługa schematu MapaGlebowoRolnicza_2026 (kompatybilność wsteczna)

> Status: ready-for-agent
> Seam testowy zaakceptowany: `SchemaDetector` + czysta funkcja kompozycji etykiety + wybór XSD; ścieżki QGIS-runtime weryfikowane manualnie / na syntetycznym GML 2026.

## Problem Statement

Wtyczka QGIS „Mapa Glebowo-Rolnicza" obsługuje wyłącznie schemat aplikacyjny GML `MapaGlebowoRolnicza_2023` (namespace `gr:…:1.0`). GUGiK wprowadził nowy schemat `MapaGlebowoRolnicza_2026` (namespace `gr:…:3.0`) ze zmienioną strukturą `opisPodloza`, nowymi wartościami atrybutów i przeniesionym `skalaMacierzysta`. Użytkownik musi móc wczytywać i walidować pliki w **obu** schematach, przy czym pliki w starym schemacie mają nadal działać bez zmian, a aplikacja ma sama rozpoznać wersję pliku.

## Solution

Wtyczka automatycznie wykrywa wersję schematu na podstawie namespace `gr` w elemencie głównym GML, waliduje plik właściwym XSD i wczytuje dane do QGIS dla obu schematów. Logika budowania etykiet `opisPodloza` rozgałęzia się per wersja; wspólny, zaktualizowany styl konturów renderuje nowe symbole (`skala` 4/5, `szkieletowosc` 3), które są nieszkodliwe dla starych danych.

## User Stories

1. Jako operator, chcę wczytać plik GML w schemacie 2023, aby stara ścieżka działała identycznie jak dotychczas (kompatybilność wsteczna).
2. Jako operator, chcę wczytać plik GML w schemacie 2026, aby korzystać z nowego schematu bez ręcznego wskazywania wersji.
3. Jako operator, chcę, aby aplikacja sama wykryła wersję schematu z namespace `gr`, abym nie musiał niczego konfigurować.
4. Jako operator, chcę, aby plik 2026 był walidowany XSD 2026, a plik 2023 — XSD 2023, aby komunikaty błędów były trafne.
5. Jako operator, chcę zobaczyć jawny błąd, gdy namespace jest nieobsługiwany (inny niż `:1.0`/`:3.0`), z podaniem wykrytego namespace, aby wiedzieć, że plik jest spoza zakresu.
6. Jako operator, chcę wczytywać kontury i odkrywki niezależnie, aby móc w jednej sesji mieć plik 2023 dla jednego typu i 2026 dla drugiego.
7. Jako operator, chcę, aby po udanej walidacji dane były wczytane do QGIS dla obu schematów, aby zobaczyć warstwę na mapie.
8. Jako kartograf, chcę widzieć symbol `○` na końcu opisu w liczniku dla `skala="4"`, aby odczytać rodzaj skały macierzystej.
9. Jako kartograf, chcę widzieć symbol `⊡` na końcu opisu w liczniku dla `skala="5"`, aby odczytać rodzaj skały macierzystej.
10. Jako kartograf, chcę, aby symbole `skala` 4/5 działały zarówno dla plików 2023, jak i 2026, aby wizualizacja była spójna.
11. Jako kartograf, chcę widzieć kopułę `⌒` (z podkreśleniem, jeśli font pozwala) po podłożu dla `szkieletowosc="3"`, aby odczytać szkieletowość.
12. Jako kartograf, chcę, aby dotychczasowe `szkieletowosc` 1/2 (podkreślenia) oraz `sz/r/sk` (tekst) działały bez zmian.
13. Jako kartograf, chcę, aby w schemacie 2026 `skalaMacierzysta` była komponowana wewnątrz `opisPodloza` (po `gatunekMady`), analogicznie do `podloze`/`gatunekMady`/`gatunekRedziny`.
14. Jako kartograf, chcę, aby w schemacie 2023 `skalaMacierzysta` nadal „zastępowała podłoże 1", aby stare mapy wyglądały identycznie.
15. Jako kartograf, chcę, aby każda wartość `numerPodloza` (`1,2,2a,3,3a,4,4a,5,5a`) miała własny, pełny slot pól (9 slotów), aby żadna z możliwych wartości `GR_TypNumerPodlozaType` nie była tracona (numerPodloza występuje realnie raz).
16. Jako kartograf, chcę, aby etykieta każdego `opisPodloza` była budowana wyłącznie z jego własnych wartości (w tym własnego `miazszosc`); `:` przy podłożu „a" pochodzi z jego `miazszosc`, dzięki czemu konkatenacja slotów w QML daje np. `ps:gs`. Brak sztucznego separatora między slotami.
17. Jako operator, chcę, aby kolejność slotów na etykiecie wynikała ze stałej kolejności `1,2,2a,3,3a,4,4a,5,5a` w wyrażeniu QML, niezależnie od kolejności w pliku.
18. Jako operator, chcę, aby pliki 2026 z liczbą `opisPodloza` > 5 (maxOccurs unbounded; do 9 wpisów) nie powodowały awarii.
19. Jako operator, chcę, aby `numerPodloza="2a"` itd. nie powodowało wyjątku (dziś `int("2a")` się wywala).
20. Jako operator, chcę, aby nowe pola 2026 (`teryt`, `typPodtypSGP6`, string `numerOdkrywkiGlebowej`) wczytywały się bez błędu.
21. Jako operator, chcę, aby styl odkrywek pozostał niezmieniony, bo nowy schemat nie zmienia jego wizualizacji.
22. Jako operator, chcę, aby zapis do `.gpkg` (z osadzonym stylem) działał dla obu schematów jak dotąd.
23. Jako maintainer, chcę widzieć podbitą wersję wtyczki (`1.1.0`) i wpis w changelog, aby oznaczyć zmianę funkcjonalną.
24. Jako maintainer, chcę mieć syntetyczny, walidujący się plik GML 2026 do weryfikacji, aby przetestować nowe przypadki.

## Implementation Decisions

- **Nowy moduł `SchemaDetector`** — czyta namespace `gr` z roota GML i zwraca obiekt wersji (enum wersji + ścieżka XSD + faktyczny URI `gr`). Namespace odczytywany dynamicznie z pliku, nie zaszyty. Mapowanie: `urn:…:1.0` → 2023, `urn:…:3.0` → 2026; inny → błąd „nieobsługiwana wersja".
- **Detekcja raz w kontrolerze (dialog)** — po wyborze pliku, niezależnie dla kontur i odkrywek; wykryty obiekt wersji wstrzykiwany do walidacji i do `display_service`. Znika zależność od globalnego `GML_NAMESPACES[:1.0]`.
- **`ValidationService`** — przyjmuje obiekt wersji; wybiera XSD wg wersji; kontrole obecności `GR_KonturGlebowy`/`GR_OdkrywkaGlebowa` używają namespace z obiektu wersji (naprawia dzisiejsze pęknięcie dla `:3.0`).
- **`DisplayService` — rozgałęzienie per wersja w kompozycji `opisPodloza`:**
  - 2023: bez zmian, w tym `skalaMacierzysta` top-level „zastępuje podłoże 1".
  - 2026: `skalaMacierzysta` per-`opisPodloza`, komponowana po `gatunekMady` (kolejność sekwencji XSD), z tą samą regułą podkreślenia szkieletowości co inne tokeny.
- **Podłoża „a" — 9 slotów** (`SLOT_KEYS = 1,2,2a,3,3a,4,4a,5,5a`): każda wartość `numerPodloza` ma własny, pełny zestaw pól i własne `etykietaOpisPodloza{wartość}`. Etykieta slotu budowana wyłącznie z wartości danego `opisPodloza`; `miazszosc` (dla slotów > pierwszego, w tym „a") jest prefiksem — `:` wpisu „a" tworzy naturalne złączenie `ps:gs` po konkatenacji slotów w QML. **Brak sztucznego separatora.**
- **Zmiana typu pola `numerPodloza{slot}`** w warstwie memory z `Int` na **String** (mieści wartości „a"; spójność 2023/2026).
- **Symbole etykiety:**
  - QML: rozszerzenie wyrażenia `CASE` o `skala` `'4'→'◯'` (U+25EF LARGE CIRCLE), `'5'→'🔳'` (U+1F533 WHITE SQUARE BUTTON); glify dobrane rozmiarem do `Δ`/`◻️` (starsze, mniejsze `'○'` U+25CB, `'⊡'` U+22A1, `'▣'` U+25A3 oraz `'⬚'` U+2B1A zachowane zakomentowane w `constants.py`); wyrażenie etykiety konkatenuje `etykietaOpisPodloza` w kolejności `1,2,2a,3,3a,4,4a,5,5a`.
  - Kod kompozycji: `szkieletowosc='3'` → doklejenie samego `⌒` (U+2312) (stała `SZKIELETOWOSC_3_LABEL`); łączące podkreślenie pod kopułą nie renderuje się poprawnie w Arial, więc po teście wizualnym zostaje sama kopuła; token bazowy niepodkreślany.
  - Nowe stałe symboli w `constants.py`.
- **Styl:** nowy `kontur_glebowy_v6.qml` (skala 4/5, kopuła, 9 pól `etykietaOpisPodloza` w wyrażeniu etykiety), wskazany przez `constants.py`. Konfiguracja formularza atrybutów dla 4 nowych slotów „a" korzysta z domyślnych widgetów QGIS (pola i tak istnieją w warstwie). **`odkrywka_glebowa_v5.qml` bez zmian.**
- **Nowe pola 2026** (`teryt`, `typPodtypSGP6`, string `numerOdkrywkiGlebowej`) przechodzą przez provider OGR automatycznie — brak dodatkowej logiki.
- **Nieznany namespace** → twardy błąd walidacji z wykrytym namespace w komunikacie; bez cichego fallbacku.
- **Wydanie:** `metadata.txt` → `1.1.0` + changelog + wzmianka o obsłudze obu schematów. `resources.py` bez rekompilacji.

## Testing Decisions

- **Co jest dobrym testem:** testujemy zachowanie zewnętrzne (wejście→wyjście), nie szczegóły implementacji. Dla logiki czystej: dana wejściowa (ścieżka/GML lub węzeł `opisPodloza`) → oczekiwany string etykiety / obiekt wersji.
- **Testowane moduły (najwyższy możliwy seam — zaakceptowany):**
  - `SchemaDetector`: namespace `:1.0`/`:3.0`/nieznany → poprawny obiekt wersji / błąd.
  - Kompozycja `etykietaOpisPodloza` (funkcja czysta, wydzielona z QGIS-runtime): przypadki 2023 (skalaMacierzysta zastępuje podłoże 1, szkieletowosc 1/2/sz/r/sk) i 2026 (podłoża „a" jako osobne sloty, `:` z `miazszosc`, skalaMacierzysta po `gatunekMady`, szkieletowosc 3 → kopuła, wszystkie 9 slotów).
  - Wybór XSD w walidacji wg wersji.
- **Prior art:** brak realnego pipeline'u testowego (istniejący `test/` to szablon Plugin Buildera wymagający pełnego środowiska QGIS). Testy jednostkowe dla logiki czystej nie wymagają QGIS i mogą działać na samym `lxml`/ElementTree.
- **Weryfikacja manualna + syntetyczny GML 2026:** ścieżki QGIS-runtime (warstwa memory, zapis `.gpkg`, aplikacja QML) weryfikowane ręcznie w QGIS na wygenerowanym, walidującym się pliku 2026 pokrywającym wszystkie nowe przypadki.

## Out of Scope

- Zmiany w wizualizacji/stylu odkrywek.
- Rekompilacja zasobów (`resources.py`) / zmiany ikon.
- Migracja/konwersja plików między schematami.
- Wsparcie dla wersji schematu innych niż 2023 i 2026.
- Worktree `.kilo/…` (osobna, starsza kopia) i starsze style `_v3/_v4/_v5`.
- Pełny automatyczny pipeline testowy dla ścieżek QGIS-runtime.

## Further Notes

- **Kopuła (`szkieletowosc='3'`):** test wizualny potwierdził, że łączące podkreślenie pod `⌒` nie renderuje się poprawnie w Arial — używamy samej kopuły `⌒`.
- **Złączenie „a" pochodzi z danych:** `:` między bazą a „a" (np. `ps:gs`) to wartość `miazszosc` wpisu „a" (`:` jest prawidłowym symbolem `GR_TypMiazszoscType`), a nie sztuczny separator. Etykieta każdego slotu jest budowana z jego własnych wartości.
- **`GR_TypPodtypGlebySGP6Type`** ma pustą restrykcję (`base=string`, brak facetów) → dopuszcza dowolny string; bez działań.
- Namespace `gr` w schemacie 2026 to `:3.0` mimo etykiety „2026" — mapowanie oparte o URI, nie o nazwę pliku.
