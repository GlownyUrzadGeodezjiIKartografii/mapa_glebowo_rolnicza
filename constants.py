"""Project constants."""

DEFAULT_COLOR = "#4d4d4d"
RED_COLOR = "red"

KONTUR_GLEBOWY_QML = "kontur_glebowy_v6.qml"
ODKRYWKA_GLEBOWA_QML = "odkrywka_glebowa_v5.qml"
SCHEMA_GML = "MapaGlebowoRolnicza_2023.xsd"
SCHEMA_GML_2 = "MapaGlebowoRolnicza_2026.xsd"

MAIN_ICON = "icon.png"
DOWNLOAD_ICON = "download.png"

# QGIS QSettings key for the last directory used in the Data Source Manager
# when loading vector layers (incl. GML). Shared read/write so the plugin's
# file dialogs and the Data Source Manager stay in sync.
LAST_VECTOR_DIR_KEY = "UI/lastVectorFileFilterDir"

# Combining Low Line  A̲
SINGLE_UNDERSCORE = '\u0332'
DOUBLE_UNDERSCORE = '\u0332\u0332'
# Combining Macron Below A̱
# SINGLE_UNDERSCORE = '\u0331'
# DOUBLE_UNDERSCORE = '\u0331\u0331'
DOT_IN_THE_MIDDLE = '·'
DOT_AS_TRIANGLE = ':·' #'∴'

# szkieletowosc == '3'
DOME = '⌓'  # ⌒ ARC
SZKIELETOWOSC_3_LABEL = DOME
# UWAGA: poniższe stałe NIE są używane w kodzie — glify skali są zaszyte
# na stałe w wyrażeniu etykiety w QML (mapaGlebRolStyle/kontur_glebowy_v6.qml,
# CASE "skala" ...). Zmiana symbolu wymaga edycji QML, nie tej stałej.
# Trzymane jako dokumentacja aktualnego wyboru.
# CIRCLE = '○'   # ○ U+25CB WHITE CIRCLE — za mały, grubość OK
# CIRCLE = '◯'   # ◯ U+25EF LARGE CIRCLE — za duży i za cienki
CIRCLE = '⭘'  # ⭘ U+2B58 HEAVY CIRCLE — grubszy niż U+25EF i nieco mniejszy (skala == '4')
SQUARE_WITH_DOT = '⊡'   # ⊡ U+22A1 SQUARED DOT — kropka OK, ale za mały
# SQUARE_WITH_DOT = '🔳'  # 🔳 U+1F533 WHITE SQUARE BUTTON — rozmiar OK, ale wypełnienie zamiast kropki
# SQUARE_WITH_DOT = '▣'   # ▣ U+25A3 WHITE SQUARE CONTAINING SMALL BLACK SQUARE — większy, znak środka kwadratowy
# SQUARE_WITH_DOT = '⧇'  # ⧇ U+29C7 SQUARED SMALL CIRCLE — kwadrat z okrągłą kropką, większy niż U+22A1 (skala == '5')

# gr application-schema namespaces per schema version
GR_NAMESPACE_2023 = 'urn:gugik:specyfikacje:gmlas:mapaGlebowoRolnicza:1.0'
GR_NAMESPACE_2026 = 'urn:gugik:specyfikacje:gmlas:mapaGlebowoRolnicza:3.0'
GML_NAMESPACE = 'http://www.opengis.net/gml/3.2'
XSI_NAMESPACE = 'http://www.w3.org/2001/XMLSchema-instance'

# Kept for backward compatibility; new code builds namespace maps per detected
# schema version via schema_detector.SchemaVersion.namespaces().
GML_NAMESPACES = {
            'gml': GML_NAMESPACE,
            'gr': GR_NAMESPACE_2023,
            'xsi': XSI_NAMESPACE
        }

VALIDATION_ERROR_INFO = "Błąd walidacji"
FILE_ERROR_INFO = "Błąd pliku"
LOAD_ERROR_INFO = "Błąd wczytania"
OK_INFO = "OK"
PROCESSING_INFO = "przetwarzanie ..."
DOTS_INFO = "..."
