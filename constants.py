"""Project constants."""

DEFAULT_COLOR = "#4d4d4d"
RED_COLOR = "red"

KONTUR_GLEBOWY_QML = "kontur_glebowy_v4.qml"
ODKRYWKA_GLEBOWA_QML = "odkrywka_glebowa_v4.qml"
SCHEMA_GML = "MapaGlebowoRolnicza.xsd"

MAIN_ICON = "icon.png"
DOWNLOAD_ICON = "download.png"

# Combining Low Line  A̲
SINGLE_UNDERSCORE = '\u0332'
DOUBLE_UNDERSCORE = '\u0332\u0332'
# Combining Macron Below A̱
# SINGLE_UNDERSCORE = '\u0331'
# DOUBLE_UNDERSCORE = '\u0331\u0331'
DOT_IN_THE_MIDDLE = '·'
DOT_AS_TRIANGLE = ':·' #'∴'

GML_NAMESPACES = {
            'gml': 'http://www.opengis.net/gml/3.2',
            'gr': 'urn:gugik:specyfikacje:gmlas:mapaGlebowoRolnicza:1.0',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }

VALIDATION_ERROR_INFO = "Błąd walidacji"
FILE_ERROR_INFO = "Błąd pliku"
LOAD_ERROR_INFO = "Błąd wczytania"
OK_INFO = "OK"
PROCESSING_INFO = "przetwarzanie ..."
DOTS_INFO = "..."
