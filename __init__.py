# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MapaGlebowoRolnicza
                                 A QGIS plugin
 Wtyczka do wizualizacji mapy glebowo rolniczej
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2024-08-13
        copyright            : (C) 2024 by GUGiK
        email                : gugik@gugik.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load MapaGlebowoRolnicza class from file MapaGlebowoRolnicza.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .mapa_glebowo_rolnicza import MapaGlebowoRolnicza
    return MapaGlebowoRolnicza(iface)
