"""Display GML module"""

import os
from qgis.core import QgsVectorLayer, QgsProject, QgsLayerTreeLayer, QgsVectorFileWriter, QgsReadWriteContext
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtXml import QDomDocument
from .constants import KONTUR_GLEBOWY_QML, ODKRYWKA_GLEBOWA_QML, LOAD_ERROR_INFO
from .opis_podloza import collect_opis_podloza, SLOT_FIELDS, SLOT_KEYS
from .compat import make_string_field


class DisplayService:
    """Display GML Service"""
    error_lokalny_id = ""

    def display_odkrywki(self, gml_path, progressBarOdkrywkiLoad):
        """Method to display odkrywki gml file"""

        try:
            base_name = os.path.basename(gml_path)
            original_layer = QgsVectorLayer(gml_path, base_name.split('.')[0], "ogr")
            if not original_layer.isValid():
                QMessageBox.critical(None, LOAD_ERROR_INFO, "Nie udało się wczytać warstwy!")
                return False

            progressBarOdkrywkiLoad.setMaximum(original_layer.featureCount())

            # Create a memory layer with the same fields as the original layer
            layer = QgsVectorLayer(f"Point?crs={original_layer.crs().authid()}", base_name.split('.')[0], "memory")
            memory_layer_data_provider = layer.dataProvider()
            memory_layer_data_provider.addAttributes(original_layer.fields())
            layer.updateFields()

            # Copy features from the original layer to the memory layer
            for feature in original_layer.getFeatures():
                progressBarOdkrywkiLoad.setValue(progressBarOdkrywkiLoad.value() + 1)
                memory_layer_data_provider.addFeature(feature)

            layer.commitChanges()

            # add style
            plugin_dir = os.path.dirname(__file__)
            layer.loadNamedStyle(os.path.join(plugin_dir, "mapaGlebRolStyle", ODKRYWKA_GLEBOWA_QML))
            layer.triggerRepaint()

            QgsProject.instance().addMapLayer(layer)

            gpkg_path = gml_path[:-3] + "gpkg"
            self.__save_layer_to_gpkg(layer, gpkg_path, "odkrywki")

            return True
        except Exception as ex:
            QMessageBox.critical(None, LOAD_ERROR_INFO, f"Nie udało się wczytać pliku gml")
            print(f"Failed to load layer: {ex}")
            return False

    def display_kontury(self, gml_path, progressBarKontury, schema_version):
        """Method to display kontury gml file"""

        try:
            base_name = os.path.basename(gml_path)
            original_layer = QgsVectorLayer(gml_path, base_name.split('.')[0], "ogr")
            if not original_layer.isValid():
                QMessageBox.critical(None, LOAD_ERROR_INFO, "Nie udało się wczytać warstwy!")
                return False

            progressBarKontury.setMaximum(original_layer.featureCount()*2)

            # Create a memory layer with the same fields as the original layer
            layer = QgsVectorLayer(f"Polygon?crs={original_layer.crs().authid()}", base_name.split('.')[0], "memory")
            memory_layer_data_provider = layer.dataProvider()
            memory_layer_data_provider.addAttributes(original_layer.fields())
            layer.updateFields()

            # Copy features from the original layer to the memory layer

            for feature in original_layer.getFeatures():
                progressBarKontury.setValue(progressBarKontury.value() + 1)
                memory_layer_data_provider.addFeature(feature)

            # add opis podloza fields
            self.__replace_opis_podloza_fields(layer)

            # collect opis podloza from gml (pure, version-aware)
            opis_podloza_items = collect_opis_podloza(gml_path, schema_version)

            # add opis podloza values
            self.__add_opis_podloza_values(layer, opis_podloza_items, progressBarKontury)

            layer.commitChanges()

            # add style
            plugin_dir = os.path.dirname(__file__)
            layer.loadNamedStyle(os.path.join(plugin_dir, "mapaGlebRolStyle", KONTUR_GLEBOWY_QML))
            layer.triggerRepaint()

            # add layer to project on the bottom
            QgsProject.instance().addMapLayer(layer, False)
            root = QgsProject.instance().layerTreeRoot()
            layer_node = QgsLayerTreeLayer(layer)
            root.addChildNode(layer_node)

            gpkg_path = gml_path[:-3] + "gpkg"
            self.__save_layer_to_gpkg(layer, gpkg_path, "kontury")

            return True
        except Exception as ex:
            error_massage = f"Nie udało się wczytać pliku gml. "
            if self.error_lokalny_id != "":
                error_massage += f"LokalnyId: {self.error_lokalny_id} "
            QMessageBox.critical(None, LOAD_ERROR_INFO, f"{error_massage}{self.error_lokalny_id}")
            print(f"Failed to load layer: {ex}")
            return False

    def __replace_opis_podloza_fields(self, layer):
        """Method to add opis podloza fields to the layer"""

        layer.startEditing()

        # remove old opis podloza fields
        fields_indices = [layer.fields().indexFromName(field) for field in SLOT_FIELDS]
        layer.deleteAttributes(fields_indices)
        layer.updateFields()

        # add new opis podloza fields, one full set per numerPodloza value
        # (1,2,2a,3,3a,4,4a,5,5a). numerPodloza is String so it holds the 2026
        # "a" values while staying compatible with 2023 integers.
        for slot in SLOT_KEYS:
            fiels_to_add = []
            for field in SLOT_FIELDS:
                fiels_to_add.append(make_string_field(f"{field}{slot}"))
            layer.dataProvider().addAttributes(fiels_to_add)
            layer.updateFields()

    def __add_opis_podloza_values(self, layer, opis_podloza_items, progressBarKontury):
        """Method to add opis podloza values to the layer"""

        layer.startEditing()
        for feature in layer.getFeatures():
            progressBarKontury.setValue(progressBarKontury.value() + 1)
            lokalny_id = feature['lokalnyId']
            if lokalny_id in opis_podloza_items:
                self.error_lokalny_id = lokalny_id
                items = opis_podloza_items[lokalny_id]
                for slot in SLOT_KEYS:
                    for field in SLOT_FIELDS:
                        key = f"{field}{slot}"
                        feature[key] = items[key] if key in items else None
                    layer.updateFeature(feature)

    def __save_layer_to_gpkg(self, layer, gpkg_path, layer_name):
        """Save a given layer to a GeoPackage file."""

        context = QgsProject.instance().transformContext()
        name = layer.name()
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.layerName = name
        options.fileEncoding = layer.dataProvider().encoding()
        options.driverName = "GPKG"
        QgsVectorFileWriter.writeAsVectorFormatV3(layer, gpkg_path, context, options)
        doc = QDomDocument()
        readWriteContext = context = QgsReadWriteContext()
        layer.exportNamedStyle(doc)
        gpkg_layer = QgsVectorLayer(f"{gpkg_path}|layername={name}", name, "ogr")
        gpkg_layer.importNamedStyle(doc)
        gpkg_layer.saveStyleToDatabase(name, "", True, "")
