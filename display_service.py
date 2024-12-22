"""Display GML module"""

import os
import xml.etree.ElementTree as ET
from qgis.core import QgsVectorLayer, QgsProject, QgsField, QgsLayerTreeLayer, QgsVectorFileWriter, QgsReadWriteContext
from qgis.PyQt.QtWidgets import QMessageBox
from PyQt5.QtCore import QVariant
from qgis.PyQt.QtXml import QDomDocument
from .constants import DOT_AS_TRIANGLE, DOT_IN_THE_MIDDLE, KONTUR_GLEBOWY_QML, ODKRYWKA_GLEBOWA_QML, SINGLE_UNDERSCORE, DOUBLE_UNDERSCORE, GML_NAMESPACES, LOAD_ERROR_INFO


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

    def display_kontury(self, gml_path, progressBarKontury):
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

            # collect opis podloza from gml
            opis_podloza_items = self.__collect_opis_podloza_from_gml(gml_path)

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

        opis_podloza_fields = [
            "numerPodloza", "podloze", 
            "szkieletowosc", "rodzajGlebyOrganicznej", 
            "miazszosc", "gatunekRedziny", "gatunekMady", 
            "informacjeDodatkowe", "etykietaOpisPodloza"
        ]

        layer.startEditing()

        # remove old opis podloza fields
        fields_indices = [layer.fields().indexFromName(field) for field in opis_podloza_fields]
        layer.deleteAttributes(fields_indices)
        layer.updateFields()

        # add new opis podloza fields
        for i in range(1, 6):
            fiels_to_add = []
            for field in opis_podloza_fields:
                q_variant = QVariant.String if field != "numerPodloza" else QVariant.Int
                fiels_to_add.append(QgsField(f"{field}{i}", q_variant))
            layer.dataProvider().addAttributes(fiels_to_add)
            layer.updateFields()

    def __collect_opis_podloza_from_gml(self, gml_path):
        """Method to collect opis podloza from gml file"""

        opis_podloza_items = {}
        tree = ET.parse(gml_path)
        root = tree.getroot()

        for feature_member in root.findall('gml:featureMember', GML_NAMESPACES):
            for kontur_glebowy_node in feature_member.findall('gr:GR_KonturGlebowy', GML_NAMESPACES):
                lokalny_id = kontur_glebowy_node.find('gr:lokalnyId', GML_NAMESPACES).text
                self.error_lokalny_id = lokalny_id
                items = {}

                # get skalaMacierzysta label with szkieletowosc if exists in podloze 1
                skala_macierzysta_etykieta = self.__create_skala_macierzysta_label(kontur_glebowy_node)
                if skala_macierzysta_etykieta is not None:
                    items[f"etykietaOpisPodloza{1}"] = skala_macierzysta_etykieta

                for opis_podloza_node in kontur_glebowy_node.findall('gr:opisPodloza', GML_NAMESPACES):
                    # populate fields and values
                    numer_podloza = self.__get_node_value_or_default(opis_podloza_node, 'gr:numerPodloza')
                    index = int(numer_podloza)

                    items[f"numerPodloza{index}"] = int(numer_podloza)

                    podloze = self.__get_node_value_or_default(opis_podloza_node, 'gr:podloze')
                    items[f"podloze{index}"] = podloze

                    szkieletowosc = self.__get_node_value_or_default(opis_podloza_node, 'gr:szkieletowosc')
                    items[f"szkieletowosc{index}"] = szkieletowosc

                    rodzajGlebyOrganicznej = self.__get_node_value_or_default(opis_podloza_node, 'gr:rodzajGlebyOrganicznej')
                    items[f"rodzajGlebyOrganicznej{index}"] = rodzajGlebyOrganicznej

                    miazszosc = self.__get_node_value_or_default(opis_podloza_node, 'gr:miazszosc')
                    items[f"miazszosc{index}"] = miazszosc

                    gatunekRedziny = self.__get_node_value_or_default(opis_podloza_node, 'gr:gatunekRedziny')
                    items[f"gatunekRedziny{index}"] = gatunekRedziny

                    gatunekMady = self.__get_node_value_or_default(opis_podloza_node, 'gr:gatunekMady')
                    items[f"gatunekMady{index}"] = gatunekMady

                    informacjeDodatkowe = self.__get_node_value_or_default(opis_podloza_node, 'gr:informacjeDodatkowe')
                    items[f"informacjeDodatkowe{index}"] = informacjeDodatkowe

                    # populate etykietaOpisPodloza - additional field and value
                    etykieta_opis_podloza = ""

                    szkieletowosc_underscore = None
                    if szkieletowosc == '1':
                        szkieletowosc_underscore = SINGLE_UNDERSCORE
                    if szkieletowosc == '2':
                        szkieletowosc_underscore = DOUBLE_UNDERSCORE
                    
                    if index > 1 and miazszosc is not None:
                        if miazszosc == '.':
                            etykieta_opis_podloza = DOT_IN_THE_MIDDLE
                        elif miazszosc == ':.':
                            etykieta_opis_podloza = DOT_AS_TRIANGLE
                        else:
                            etykieta_opis_podloza = miazszosc

                    if podloze is not None:
                        if szkieletowosc_underscore is None:
                            etykieta_opis_podloza += podloze
                        else:
                            etykieta_opis_podloza += podloze[:-1] + podloze[-1] + szkieletowosc_underscore
                    if rodzajGlebyOrganicznej is not None:
                        if szkieletowosc_underscore is None:
                            etykieta_opis_podloza += rodzajGlebyOrganicznej
                        else:
                            etykieta_opis_podloza += rodzajGlebyOrganicznej[:-1] + rodzajGlebyOrganicznej[-1] + szkieletowosc_underscore
                    if gatunekRedziny is not None:
                        if szkieletowosc_underscore is None:
                            etykieta_opis_podloza += gatunekRedziny
                        else:
                            szkieletowosc_underscore_index = -2 if ')' in gatunekRedziny else -1
                            gatunek_redziny_char_list = list(gatunekRedziny)
                            gatunek_redziny_char_list[szkieletowosc_underscore_index] = gatunek_redziny_char_list[szkieletowosc_underscore_index]+szkieletowosc_underscore
                            etykieta_opis_podloza += "".join(gatunek_redziny_char_list)
                    if gatunekMady is not None:
                        if szkieletowosc_underscore is None:
                            etykieta_opis_podloza += gatunekMady
                        else:
                            etykieta_opis_podloza += gatunekMady[:-1] + gatunekMady[-1] + szkieletowosc_underscore
                    if szkieletowosc not in [None, '1', '2']:
                        etykieta_opis_podloza += szkieletowosc

                    if f"etykietaOpisPodloza{index}" in items:
                        items[f"etykietaOpisPodloza{index}"] += etykieta_opis_podloza
                    else:
                        items[f"etykietaOpisPodloza{index}"] = etykieta_opis_podloza

                opis_podloza_items[lokalny_id] = items
        return opis_podloza_items

    def __add_opis_podloza_values(self, layer, opis_podloza_items, progressBarKontury):
        """Method to add opis podloza values to the layer"""

        layer.startEditing()
        for feature in layer.getFeatures():
            progressBarKontury.setValue(progressBarKontury.value() + 1)
            lokalny_id = feature['lokalnyId']
            if lokalny_id in opis_podloza_items:
                items = opis_podloza_items[lokalny_id]
                for i in range(1, 6):
                    feature[f"numerPodloza{i}"] = items[f"numerPodloza{i}"] if f"numerPodloza{i}" in items else None
                    feature[f"podloze{i}"] = items[f"podloze{i}"] if f"podloze{i}" in items else None
                    feature[f"szkieletowosc{i}"] = items[f"szkieletowosc{i}"] if f"szkieletowosc{i}" in items else None
                    feature[f"rodzajGlebyOrganicznej{i}"] = items[f"rodzajGlebyOrganicznej{i}"] if f"rodzajGlebyOrganicznej{i}" in items else None
                    feature[f"miazszosc{i}"] = items[f"miazszosc{i}"] if f"miazszosc{i}" in items else None
                    feature[f"gatunekRedziny{i}"] = items[f"gatunekRedziny{i}"] if f"gatunekRedziny{i}" in items else None
                    feature[f"gatunekMady{i}"] = items[f"gatunekMady{i}"] if f"gatunekMady{i}" in items else None
                    feature[f"informacjeDodatkowe{i}"] = items[f"informacjeDodatkowe{i}"] if f"informacjeDodatkowe{i}" in items else None
                    feature[f"etykietaOpisPodloza{i}"] = items[f"etykietaOpisPodloza{i}"] if f"etykietaOpisPodloza{i}" in items else None
                    layer.updateFeature(feature)

    def __create_skala_macierzysta_label(self, kontur_glebowy_node):
        """Method to create skala macierzysta label"""

        skala_macierzysta_etykieta = None
        szkieletowosc_underscore = None
        skalaMacierzysta = self.__get_node_value_or_default(kontur_glebowy_node, 'gr:skalaMacierzysta')
        for opis_podloza_node in kontur_glebowy_node.findall('gr:opisPodloza', GML_NAMESPACES):
            numer_podloza = self.__get_node_value_or_default(opis_podloza_node, 'gr:numerPodloza')
            if int(numer_podloza) != 1:
                continue
            szkieletowosc = self.__get_node_value_or_default(opis_podloza_node, 'gr:szkieletowosc')
            if szkieletowosc == '1':
                szkieletowosc_underscore = SINGLE_UNDERSCORE
            if szkieletowosc == '2':
                szkieletowosc_underscore = DOUBLE_UNDERSCORE

        if skalaMacierzysta is not None:
            if szkieletowosc_underscore is None:
                skala_macierzysta_etykieta = skalaMacierzysta
            else:
                skala_macierzysta_etykieta = skalaMacierzysta[:-1] + skalaMacierzysta[-1] + szkieletowosc_underscore
        return skala_macierzysta_etykieta

    def __save_layer_to_gpkg(self, layer, gpkg_path, layer_name):
        """Save a given layer to a GeoPackage file."""

        context = QgsProject.instance().transformContext()
        name = layer.name()
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.layerName = name
        options.fileEncoding = layer.dataProvider().encoding()
        options.driverName = "GPKG"
        QgsVectorFileWriter.writeAsVectorFormatV2(layer, gpkg_path, context, options)
        doc = QDomDocument()
        readWriteContext = context = QgsReadWriteContext()
        layer.exportNamedStyle(doc)
        gpkg_layer = QgsVectorLayer(f"{gpkg_path}|layername={name}", name, "ogr")
        gpkg_layer.importNamedStyle(doc)
        gpkg_layer.saveStyleToDatabase(name, "", True, "")

    def __get_node_value_or_default(self, node, tag):
        """Method to get node value or default"""

        node_element = node.find(tag, GML_NAMESPACES)
        node_value = node_element.text if node_element is not None else None
        return node_value
