"""Moduł walidacji GML.

Walidacja raportuje **wszystkie** znalezione błędy zamiast przerywać na
pierwszym:

* każdy ``gml:featureMember`` walidowany jest niezależnie, więc błąd w jednym
  obiekcie nie blokuje pozostałych;
* w obrębie jednego obiektu silnik ``xmlschema`` raportuje w komplecie zarówno
  błędy wartości/typów, jak i błędy *strukturalne* (brak/nadmiarowy element,
  zła kolejność) — dlatego dwa błędy w jednym obiekcie dają dwa wpisy, a nie
  jeden;
* dodatkowy przebieg na całym dokumencie wychwytuje błędy na poziomie pliku
  (korzeń/root), czyli błędy spoza obiektów, które trafiają pod klucz ``plik``.

Walidator ``xmlschema`` jest zwendorowany w katalogu ``libs`` (wraz z zależnością
``elementpath``) — dołączany jest do ``sys.path`` przy imporcie tego modułu, bo
środowisko QGIS go nie zawiera. Schemat budowany jest w trybie ``allow='local'``
— korzysta wyłącznie z lokalnie zwendorowanego zestawu GML (``schema/ogc``), bez
cichego pobierania z sieci.

``validate_*`` nigdy nie zwraca ``None`` dla błędów — zawsze słownik
(``{klucz: [rekord, ...]}``), gdzie rekord to ``{'linia', 'element',
'komunikat'}``. Dzięki temu ``len(errors)`` po stronie dialogu jest zawsze
bezpieczne.
"""

import os
import sys

from lxml.etree import XMLParser, parse
from qgis.PyQt.QtWidgets import QMessageBox

# Walidator ``xmlschema`` (+ zależność ``elementpath``) jest zwendorowany lokalnie,
# bo Python QGIS-a ich nie dostarcza. Dokładamy katalog ``libs`` do ścieżki importu.
_LIBS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libs')
if _LIBS_DIR not in sys.path:
    sys.path.insert(0, _LIBS_DIR)

import xmlschema  # noqa: E402  (import po modyfikacji sys.path)

from .constants import (  # noqa: E402
    FILE_ERROR_INFO,
    GML_NAMESPACE,
    GML_NAMESPACES,
    GR_NAMESPACE_2023,
    GR_NAMESPACE_2026,
    VALIDATION_ERROR_INFO,
    XSI_NAMESPACE,
)

GML_ID_ATTR = '{%s}id' % GML_NAMESPACE
FILE_KEY = 'plik'

_SAFE_PARSER = XMLParser(resolve_entities=False, load_dtd=False, no_network=True)

# Odwzorowanie URI przestrzeni nazw na prefiks, do czytelnego nazywania elementów
# w raporcie. ``gr`` celowo mapuje obie wersje schematu (2023 i 2026).
_NS_PREFIXES = {
    GML_NAMESPACE: 'gml',
    GR_NAMESPACE_2023: 'gr',
    GR_NAMESPACE_2026: 'gr',
    XSI_NAMESPACE: 'xsi',
}


class ValidationService:
    """Usługa walidacji GML."""

    def __init__(self):
        # Budowa schematu GML (z importami GML 3.2.1) trwa ~1 s, więc cache'ujemy
        # go per ścieżka XSD — kontury i odkrywki często używają tego samego pliku.
        self._schema_cache = {}

    def validate_kontury_with_schema(self, gml_path, schema_path, progressBarControle, namespaces=None):
        """Waliduje kontury GML i plik GML za pomocą schematu.

        ``namespaces`` to mapa przestrzeni nazw dla wykrytej wersji schematu
        (identyfikator URI gr różni się między wersjami 2023 i 2026); domyślnie
        używana jest starsza mapa z 2023 roku dla zachowania kompatybilności.
        """

        return self.__validate(
            gml_path, schema_path, progressBarControle, namespaces,
            feature_tag='gr:GR_KonturGlebowy',
            missing_message='Brak konturów glebowych [gr:GR_KonturGlebowy] w pliku gml')

    def validate_odkrywki_with_schema(self, gml_path, schema_path, progressBarControle, namespaces=None):
        """Waliduje odkrywki GML i plik GML za pomocą schematu.

        ``namespaces`` to mapa przestrzeni nazw dla wykrytej wersji schematu;
        domyślnie używana jest starsza mapa z 2023 roku dla zachowania
        kompatybilności.
        """

        return self.__validate(
            gml_path, schema_path, progressBarControle, namespaces,
            feature_tag='gr:GR_OdkrywkaGlebowa',
            missing_message='Brak odkrywek glebowych [gr:GR_OdkrywkaGlebowa] w pliku gml')

    def __validate(self, gml_path, schema_path, progressBarControle, namespaces, feature_tag, missing_message):
        """Wspólna ścieżka walidacji dla konturów i odkrywek.

        Zwraca ``(ok, errors)``; ``errors`` jest zawsze słownikiem (nigdy
        ``None``).
        """

        namespaces = namespaces or GML_NAMESPACES

        try:
            schema = self.__build_schema(schema_path)
        except Exception as e:
            print(e)
            QMessageBox.critical(None, VALIDATION_ERROR_INFO,
                                 "Nie udało się zbudować schematu XSD (walidacja offline).")
            return False, {FILE_KEY: [self.__hard_error(f"Nie udało się zbudować schematu XSD: {e}")]}

        try:
            tree = parse(gml_path, _SAFE_PARSER)
        except Exception as e:
            print(e)
            QMessageBox.critical(None, FILE_ERROR_INFO, "Nie udało się otworzyć pliku gml")
            return False, {FILE_KEY: [self.__hard_error(f"Nie udało się otworzyć pliku gml: {e}")]}

        errors = self.__collect_errors(schema, tree, progressBarControle)

        if not self.__feature_present(tree.getroot(), feature_tag, namespaces):
            errors.setdefault(FILE_KEY, []).append(self.__hard_error(missing_message))
            QMessageBox.critical(None, FILE_ERROR_INFO, missing_message)

        if errors:
            QMessageBox.critical(
                None, VALIDATION_ERROR_INFO,
                f"Wskazany plik gml nie waliduje się. Liczba obiektów/sekcji z błędami: {len(errors)}")
            return False, errors

        return True, {}

    def __build_schema(self, schema_path):
        """Buduje (i cache'uje) schemat XSD wyłącznie z lokalnych plików.

        ``allow='local'`` blokuje pobieranie zdalnych lokalizacji — importy GML
        (``schema/ogc``) mają ścieżki względne, więc rozwiązują się lokalnie.
        """

        schema = self._schema_cache.get(schema_path)
        if schema is None:
            schema = xmlschema.XMLSchema(schema_path, allow='local')
            self._schema_cache[schema_path] = schema
        return schema

    def __collect_errors(self, schema, tree, progressBarControle):
        """Zbiera wszystkie błędy: poziom pliku + każdy obiekt niezależnie.

        ``xmlschema.iter_errors`` nie urywa się na pierwszym błędzie, więc dla
        jednego obiektu zwracane są wszystkie naruszenia (wartości i struktury).
        """

        errors = {}
        root = tree.getroot()
        if root is None:
            return errors

        feature_members = [el for el in tree.iter() if str(el.tag).endswith('featureMember')]

        # Pasek postępu: jeden krok na przebieg dokumentowy + po jednym na obiekt.
        progressBarControle.setMaximum(len(feature_members) + 1)

        # Przebieg na całym dokumencie — wychwytuje błędy na poziomie pliku/korzenia.
        # Zostawiamy tylko błędy spoza obiektów (bez przodka ``featureMember``),
        # by nie dublować walidacji per-obiekt.
        progressBarControle.setValue(progressBarControle.value() + 1)
        for error in schema.iter_errors(tree):
            if self.__nearest_feature_member(getattr(error, 'elem', None)) is None:
                errors.setdefault(FILE_KEY, []).append(self.__record(error))

        # Przebieg per-obiekt — każdy ``featureMember`` walidowany niezależnie.
        for feature_member in feature_members:
            progressBarControle.setValue(progressBarControle.value() + 1)
            key = self.__object_key(feature_member)
            for error in schema.iter_errors(feature_member):
                errors.setdefault(key, []).append(self.__record(error))

        return errors

    def __feature_present(self, root, feature_tag, namespaces):
        """Czy w pliku występuje przynajmniej jeden obiekt oczekiwanego typu."""

        if root is None:
            return False
        for feature_member in root.findall('gml:featureMember', namespaces):
            if feature_member.find(feature_tag, namespaces) is not None:
                return True
        return False

    def __object_key(self, feature_member):
        """Klucz obiektu: ``gml:id`` jeśli jest, w przeciwnym razie ``obiekt@linia{n}``."""

        for element in feature_member.iter():
            gml_id = element.get(GML_ID_ATTR)
            if gml_id:
                return gml_id
        return f"obiekt@linia{feature_member.sourceline or '?'}"

    def __nearest_feature_member(self, element):
        """Najbliższy przodek ``featureMember`` danego elementu (lub ``None``)."""

        node = element
        while node is not None:
            if str(node.tag).endswith('featureMember'):
                return node
            node = node.getparent()
        return None

    def __record(self, error):
        """Buduje rekord błędu ``{'linia', 'element', 'komunikat'}`` z błędu xmlschema."""

        element = getattr(error, 'elem', None)
        line = getattr(error, 'sourceline', None)
        if line is None and element is not None:
            line = element.sourceline
        element_name = self.__format_qname(str(element.tag)) if element is not None else ''
        message = getattr(error, 'reason', None) or 'błąd walidacji'
        return {'linia': line, 'element': element_name, 'komunikat': message}

    def __hard_error(self, message):
        """Rekord błędu bez przypisania do linii/elementu (np. awaria schematu)."""

        return {'linia': None, 'element': '', 'komunikat': message}

    def __format_qname(self, raw):
        """Zamienia ``{uri}nazwa`` na ``prefiks:nazwa`` (lub samą nazwę, gdy URI nieznane)."""

        if raw.startswith('{') and '}' in raw:
            uri, local = raw[1:].split('}', 1)
            prefix = _NS_PREFIXES.get(uri)
            return f"{prefix}:{local}" if prefix else local
        return raw

    def save_errors_to_file(self, errors, file_path):
        """Zapisuje błędy walidacji do czytelnego pliku tekstowego (UTF-8).

        Błędy są grupowane po obiekcie; sekcja ``Plik`` (błędy na poziomie
        dokumentu) trafia na koniec.
        """

        errors = errors or {}
        with open(file_path, 'w', encoding='utf-8') as file:
            for key, records in errors.items():
                if key == FILE_KEY:
                    continue
                file.write(f"Obiekt: {key}\n")
                for record in records:
                    file.write(self.__format_report_line(record))
                file.write("\n")
            if FILE_KEY in errors:
                file.write("Plik:\n")
                for record in errors[FILE_KEY]:
                    file.write(self.__format_report_line(record))
                file.write("\n")

    def __format_report_line(self, record):
        """Formatuje pojedynczy wiersz raportu: ``  [linia X] element: komunikat``."""

        linia = f"[linia {record['linia']}] " if record.get('linia') else ""
        element = f"{record['element']}: " if record.get('element') else ""
        return f"  {linia}{element}{record['komunikat']}\n"
