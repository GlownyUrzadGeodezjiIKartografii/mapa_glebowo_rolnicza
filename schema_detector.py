"""Automatyczne wykrywanie wersji schematu.

Odczytuje przestrzeń nazw schematu aplikacyjnego ``gr`` z elementu głównego GML
i mapuje ją na :class:`SchemaVersion` (identyfikator wersji, nazwa pliku XSD
oraz rzeczywisty identyfikator URI przestrzeni nazw ``gr``). Przestrzeń nazw
jest odczytywana dynamicznie z pliku, a nie zapisana na stałe, dzięki czemu
wykryty identyfikator URI jest używany przez kolejne usługi do budowania map
przestrzeni nazw.

Mapowanie: ``...:1.0`` -> 2023, ``...:3.0`` -> 2026. Każda inna wartość
powoduje zgłoszenie :class:`UnsupportedSchemaError` (bez cichego użycia
wartości zastępczej).
"""

from dataclasses import dataclass

from lxml.etree import XMLParser, parse

try:
    from .constants import (
        GR_NAMESPACE_2023,
        GR_NAMESPACE_2026,
        GML_NAMESPACE,
        XSI_NAMESPACE,
        SCHEMA_GML,
        SCHEMA_GML_2,
    )
except ImportError:
    from constants import (
        GR_NAMESPACE_2023,
        GR_NAMESPACE_2026,
        GML_NAMESPACE,
        XSI_NAMESPACE,
        SCHEMA_GML,
        SCHEMA_GML_2,
    )

SCHEMA_2023 = "2023"
SCHEMA_2026 = "2026"

# Znacznik obecny w każdym identyfikatorze URI przestrzeni nazw schematu
# aplikacyjnego gr; używany w ostateczności do znalezienia przestrzeni nazw gr,
# jeśli została zadeklarowana bez standardowego prefiksu ``gr``.
_GR_NAMESPACE_MARKER = "mapaGlebowoRolnicza"

_SAFE_PARSER = XMLParser(resolve_entities=False, load_dtd=False, no_network=True)


@dataclass(frozen=True)
class SchemaVersion:
    """Obsługiwana wersja schematu i wszystkie dane potrzebne do jej użycia."""

    version: str          # "2023" | "2026"
    xsd_filename: str      # np. "MapaGlebowoRolnicza_2023.xsd"
    gr_namespace: str      # rzeczywisty identyfikator URI odczytany z pliku

    def namespaces(self):
        """Mapa przestrzeni nazw ElementTree/lxml dla tej wersji."""
        return {
            "gml": GML_NAMESPACE,
            "gr": self.gr_namespace,
            "xsi": XSI_NAMESPACE,
        }


_REGISTRY = {
    GR_NAMESPACE_2023: SchemaVersion(SCHEMA_2023, SCHEMA_GML, GR_NAMESPACE_2023),
    GR_NAMESPACE_2026: SchemaVersion(SCHEMA_2026, SCHEMA_GML_2, GR_NAMESPACE_2026),
}


class UnsupportedSchemaError(Exception):
    """Zgłaszany, gdy GML deklaruje nieobsługiwaną przestrzeń nazw gr."""

    def __init__(self, namespace):
        self.namespace = namespace
        shown = namespace if namespace else "brak"
        super().__init__(
            "Nieobsługiwana wersja schematu (namespace: {}).".format(shown)
        )


def _extract_gr_namespace(gml_path):
    """Zwraca identyfikator URI przestrzeni nazw gr z GML albo ``None``."""
    root = parse(gml_path, _SAFE_PARSER).getroot()
    namespace_map = root.nsmap or {}
    gr_namespace = namespace_map.get("gr")
    if gr_namespace:
        return gr_namespace
    # Wartość zastępcza: gr zadeklarowane pod innym prefiksem (lub bez niego).
    for uri in namespace_map.values():
        if uri and _GR_NAMESPACE_MARKER in uri:
            return uri
    return None


def detect_schema_version(gml_path):
    """Wykrywa :class:`SchemaVersion` dla pliku GML.

    Zgłasza :class:`UnsupportedSchemaError` dla nieznanej lub brakującej
    przestrzeni nazw gr.
    """
    gr_namespace = _extract_gr_namespace(gml_path)
    version = _REGISTRY.get(gr_namespace)
    if version is None:
        raise UnsupportedSchemaError(gr_namespace)
    return version
