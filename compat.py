"""QGIS/Qt version compatibility helpers.

Single place for logic that differs between QGIS 3 (Qt5/PyQt5) and
QGIS 4 (Qt6/PyQt6). Importing everything through ``qgis.PyQt`` already
hides most PyQt5/PyQt6 differences; what remains are a few QGIS API
changes that depend on the running version.
"""

from qgis.core import Qgis, QgsField


def _qgis_version_int():
    """Return the running QGIS version as an int, e.g. 3.28 -> 32800."""
    return Qgis.versionInt()


def make_string_field(name):
    """Create a string ``QgsField`` in a version-portable way.

    QGIS 3.38 introduced a ``QgsField`` constructor based on
    ``QMetaType.Type`` and deprecated the old ``QVariant.Type`` one.
    PyQt6 (QGIS 4) also scopes enums, which makes the legacy
    ``QVariant.String`` access brittle. So on 3.38+ we use the
    ``QMetaType`` constructor; on 3.28-3.36 we fall back to ``QVariant``.
    """
    if _qgis_version_int() >= 33800:
        from qgis.PyQt.QtCore import QMetaType
        return QgsField(name, QMetaType.Type.QString)

    from qgis.PyQt.QtCore import QVariant
    return QgsField(name, QVariant.String)
