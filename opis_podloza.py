"""Zbieranie danych ``opisPodloza`` i składanie etykiet bez efektów ubocznych.

To złożone i podatne na błędy centrum obsługi konturów, wydzielone z
``DisplayService``, aby można było je testować jednostkowo bez uruchamiania QGIS
(używa tylko lxml i stałych). ``DisplayService`` wywołuje funkcję
:func:`collect_opis_podloza` i zapisuje zwrócone dane dla poszczególnych wartości
``lokalnyId`` w polach warstwy pamięciowej.

Ta sama ścieżka kodu obsługuje obie wersje schematu; różnice wynikają ze
struktury danych, a nie z jawnego rozgałęzienia:

* W 2023 ``skalaMacierzysta`` pozostaje elementem na poziomie konturu, więc
  staje się prefiksem ``etykietaOpisPodloza1`` (historyczna reguła
  „skalaMacierzysta zastępuje podłoże 1”). W 2026 tego elementu nie ma na
  poziomie konturu, więc prefiks jest naturalnie pusty.
* W 2026 ``skalaMacierzysta`` jest przeniesiona do ``opisPodloza`` i składana
  jako token za ``gatunekMady``. W 2023 tego elementu podrzędnego nie ma, więc
  nic nie jest dodawane.
* Niezależnie od etykiety ``skalaMacierzysta`` jest też surowym polem per-miejsce
  (``skalaMacierzysta1..5a``, tak jak ``numerPodloza``). W 2026 wypełnia je
  :func:`_store_raw_fields` z węzła ``opisPodloza``. W 2023 element jest na
  poziomie konturu (jeden), więc jego surowa wartość trafia do
  ``skalaMacierzysta1``; prefiks etykiety z 2023 pozostaje bez zmian.
* ``szkieletowosc == '3'`` (tylko 2026) dodaje kopułę; wartości ``skala`` 4/5
  są obsługiwane w wyrażeniu etykiety QML. W poprawnych danych 2023 obie reguły
  pozostają nieaktywne.
* Wartości ``numerPodloza`` ``2a/3a/4a/5a`` (tylko 2026) otrzymują własne
  miejsca (:data:`SLOT_KEYS`). Wartość numerPodloza występuje najwyżej raz,
  więc każda wartość mapuje się na pełny zestaw pól. Etykieta każdego miejsca
  jest składana wyłącznie z wartości danego wpisu, w tym z jego własnego
  ``miazszosc``, którego ``:`` oznacza ten sam przedział głębokości i pozwala
  wyświetlić np. ``ps`` (miejsce 4) + ``:gs`` (miejsce 4a) jako ``ps:gs`` po
  połączeniu etykiet poszczególnych miejsc przez QML. Pomiędzy miejscami nie ma
  sztucznego separatora.

Wersja schematu służy do zbudowania właściwej mapy przestrzeni nazw
(identyfikator URI przestrzeni nazw gr różni się między wersjami) i nie jest
wykorzystywana do innych rozgałęzień.
"""

from lxml.etree import XMLParser, parse

try:  # wewnątrz pakietu wtyczki QGIS
    from .constants import (
        DOT_AS_TRIANGLE,
        DOT_IN_THE_MIDDLE,
        SINGLE_UNDERSCORE,
        DOUBLE_UNDERSCORE,
        SZKIELETOWOSC_3_LABEL,
    )
except ImportError:  # tryb niezależny (testy / zwykły Python)
    from constants import (
        DOT_AS_TRIANGLE,
        DOT_IN_THE_MIDDLE,
        SINGLE_UNDERSCORE,
        DOUBLE_UNDERSCORE,
        SZKIELETOWOSC_3_LABEL,
    )

# Każda możliwa wartość numerPodloza (GR_TypNumerPodlozaType). Każda mapuje się
# na własny pełny zestaw pól / miejsce etykiety; numerPodloza występuje najwyżej
# raz w jednym konturze.
SLOT_KEYS = ["1", "2", "2a", "3", "3a", "4", "4a", "5", "5a"]

# Bazowe nazwy surowych pól dla każdego podłoża, zapisywane w warstwie
# pamięciowej dla danego miejsca.
RAW_FIELDS = [
    "numerPodloza", "podloze", "szkieletowosc", "rodzajGlebyOrganicznej",
    "miazszosc", "gatunekRedziny", "gatunekMady", "skalaMacierzysta",
    "informacjeDodatkowe",
]
# Wszystkie bazowe nazwy pól miejsc, w tym składana etykieta. Współdzielone z
# DisplayService, aby lista pól była zdefiniowana tylko raz.
SLOT_FIELDS = RAW_FIELDS + ["etykietaOpisPodloza"]

_SAFE_PARSER = XMLParser(resolve_entities=False, load_dtd=False, no_network=True)


def collect_opis_podloza(gml_path, schema_version):
    """Zwraca ``{lokalnyId: {field_name: value, ...}}`` dla każdego konturu.

    Słownik danych zawiera surowe pola ``*{n}`` oraz złożoną etykietę
    ``etykietaOpisPodloza{n}``, gotowe do zapisania w obiektach warstwy.
    """
    namespaces = schema_version.namespaces()
    root = parse(gml_path, _SAFE_PARSER).getroot()

    result = {}
    for feature_member in root.findall("gml:featureMember", namespaces):
        for kontur in feature_member.findall("gr:GR_KonturGlebowy", namespaces):
            lokalny_id = _text(kontur, "gr:lokalnyId", namespaces)
            result[lokalny_id] = _collect_kontur(kontur, namespaces)
    return result


def _collect_kontur(kontur, namespaces):
    """Zbiera pola i etykiety ``opisPodloza`` z pojedynczego konturu."""
    items = {}

    # 2023: skalaMacierzysta na poziomie konturu jest prefiksem
    # etykietaOpisPodloza1.
    # 2026: brak takiego elementu -> prefiks to None i tutaj nic się nie dzieje.
    skala_prefix = _skala_macierzysta_prefix(kontur, namespaces)
    if skala_prefix is not None:
        items["etykietaOpisPodloza1"] = skala_prefix

    for node in kontur.findall("gr:opisPodloza", namespaces):
        slot = _text(node, "gr:numerPodloza", namespaces)
        if slot is None:
            continue
        base, _is_a = _parse_numer(slot)
        _store_raw_fields(items, node, namespaces, slot)
        token = _compose_subsoil_token(node, namespaces, base)
        _append_to_label(items, slot, token)

    # 2023: skalaMacierzysta jest elementem na poziomie konturu, więc jej surowa
    # wartość trafia do skalaMacierzysta1. Ustawiane po pętli, aby nie nadpisał
    # go None zapisany przez _store_raw_fields dla węzła o numerPodloza = 1.
    # W 2026 elementu tego na poziomie konturu nie ma, więc warunek nie zachodzi.
    kontur_skala = _text(kontur, "gr:skalaMacierzysta", namespaces)
    if kontur_skala is not None:
        items["skalaMacierzysta1"] = kontur_skala

    return items


def _parse_numer(numer):
    """Dzieli numerPodloza na (indeks bazowy, is_a). „4a” -> (4, True)."""
    if numer is None:
        return 0, False
    is_a = numer.endswith("a")
    digits = numer[:-1] if is_a else numer
    try:
        base = int(digits)
    except (TypeError, ValueError):
        base = 0
    return base, is_a


def _compose_subsoil_token(node, namespaces, base):
    """Składa token etykiety na podstawie danych jednego ``opisPodloza``."""
    podloze = _text(node, "gr:podloze", namespaces)
    szkieletowosc = _text(node, "gr:szkieletowosc", namespaces)
    rodzaj_gleby_organicznej = _text(node, "gr:rodzajGlebyOrganicznej", namespaces)
    miazszosc = _text(node, "gr:miazszosc", namespaces)
    gatunek_redziny = _text(node, "gr:gatunekRedziny", namespaces)
    gatunek_mady = _text(node, "gr:gatunekMady", namespaces)
    skala_macierzysta = _text(node, "gr:skalaMacierzysta", namespaces)

    underscore = _szkieletowosc_underscore(szkieletowosc)

    label = ""
    # Każdy opisPodloza ma własny znacznik głębokości (miazszosc). Podłoża poniżej
    # pierwszego (base > 1, w tym warianty „a”) otrzymują ten prefiks; znak „:”
    # wpisu „a” wizualnie łączy go z wpisem bazowym po połączeniu etykiet.
    if base > 1 and miazszosc is not None:
        label += _miazszosc_marker(miazszosc)

    if podloze is not None:
        label += _with_underscore(podloze, underscore)
    if rodzaj_gleby_organicznej is not None:
        label += _with_underscore(rodzaj_gleby_organicznej, underscore)
    if gatunek_redziny is not None:
        label += _redziny_with_underscore(gatunek_redziny, underscore)
    if gatunek_mady is not None:
        label += _with_underscore(gatunek_mady, underscore)
    # 2026: skalaMacierzysta jest składana za gatunekMady, tak jak inne tokeny.
    if skala_macierzysta is not None:
        label += _with_underscore(skala_macierzysta, underscore)

    # Końcowa szkieletowosc: „3” -> kopuła, tekst dosłowny dla sz/r/sk,
    # brak dodatku dla 1/2.
    if szkieletowosc == "3":
        label += SZKIELETOWOSC_3_LABEL
    elif szkieletowosc not in (None, "1", "2"):
        label += szkieletowosc

    return label


def _append_to_label(items, slot, token):
    """Dodaje token do etykiety przypisanej do wskazanego miejsca."""
    key = "etykietaOpisPodloza{}".format(slot)
    existing = items.get(key)  # 2023 skalaMacierzysta jako prefiks miejsca "1", w przeciwnym razie None
    items[key] = token if existing is None else existing + token


def _store_raw_fields(items, node, namespaces, slot):
    """Zapisuje surowe pola ``opisPodloza`` w słowniku danych miejsca."""
    for field in RAW_FIELDS:
        items["{}{}".format(field, slot)] = _text(node, "gr:" + field, namespaces)


def _skala_macierzysta_prefix(kontur, namespaces):
    """2023: skalaMacierzysta z poziomu konturu z podkreśleniem zależnym od szkieletowosc podłoża 1."""
    skala_macierzysta = _text(kontur, "gr:skalaMacierzysta", namespaces)
    if skala_macierzysta is None:
        return None
    underscore = None
    for node in kontur.findall("gr:opisPodloza", namespaces):
        base, _is_a = _parse_numer(_text(node, "gr:numerPodloza", namespaces))
        if base != 1:
            continue
        underscore = _szkieletowosc_underscore(_text(node, "gr:szkieletowosc", namespaces))
    return _with_underscore(skala_macierzysta, underscore)


def _szkieletowosc_underscore(szkieletowosc):
    """Zwraca znak podkreślenia odpowiadający wartości szkieletowosci."""
    if szkieletowosc == "1":
        return SINGLE_UNDERSCORE
    if szkieletowosc == "2":
        return DOUBLE_UNDERSCORE
    return None


def _miazszosc_marker(miazszosc):
    """Zamienia oznaczenie miąższości na znak używany w etykiecie."""
    if miazszosc == ".":
        return DOT_IN_THE_MIDDLE
    if miazszosc == ":.":
        return DOT_AS_TRIANGLE
    return miazszosc


def _with_underscore(token, underscore):
    """Zwraca token z dołączonym znakiem podkreślenia, jeśli go podano."""
    if underscore is None:
        return token
    return token + underscore


def _redziny_with_underscore(token, underscore):
    """gatunekRedziny: końcowy znak „)” przesuwa podkreślenie na poprzedni znak."""
    if underscore is None:
        return token
    index = -2 if ")" in token else -1
    chars = list(token)
    chars[index] = chars[index] + underscore
    return "".join(chars)


def _text(node, tag, namespaces):
    """Zwraca tekst elementu o podanym tagu albo ``None``, jeśli go brakuje."""
    element = node.find(tag, namespaces)
    return element.text if element is not None else None
