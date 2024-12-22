import os

import xml.etree.ElementTree as ET
from qgis.core import QgsVectorLayer, QgsProject, QgsField
from qgis.PyQt.QtWidgets import QMessageBox
from PyQt5.QtCore import QVariant
from PyQt5.QtWidgets import QFileDialog, QDialog, QVBoxLayout, QPushButton, QLabel, QLineEdit, QHBoxLayout


class Displayer:
    def display_odkrywki(self, gml_path):
        try:
            base_name = os.path.basename(gml_path)      
            layer = QgsVectorLayer(gml_path, base_name.split('.')[0], "ogr")
            if not layer.isValid():
                QMessageBox.critical(None, "Błąd wczytywania", "Nie udało się wczytać warstwy!")
                return False
            plugin_dir = os.path.dirname(__file__)
            layer.loadNamedStyle(os.path.join(plugin_dir, "mapaGlebRolStyle", "odkrywka_glebowa_v3.qml"))
            layer.triggerRepaint()
            
            QgsProject.instance().addMapLayer(layer)
            return True
        except Exception as ex:
            QMessageBox.critical(None, "Błąd wczytywania", f"Nie udało się wczytać pliku gml: {ex}")
            print(f"Failed to load layer: {ex}")
            return False
    
    def display_kontury(self, gml_path):
        try:
            base_name = os.path.basename(gml_path)
            original_layer = QgsVectorLayer(gml_path, base_name.split('.')[0], "ogr")
            if not original_layer.isValid():
                QMessageBox.critical(None, "Błąd wczytywania", "Nie udało się wczytać warstwy!")
                return False
            
            # Create a memory layer with the same fields as the original layer
            layer = QgsVectorLayer(f"Polygon?crs={original_layer.crs().authid()}", base_name.split('.')[0], "memory")
            memory_layer_data_provider = layer.dataProvider()
            memory_layer_data_provider.addAttributes(original_layer.fields())
            layer.updateFields()
            
            # Copy features from the original layer to the memory layer
            for feature in original_layer.getFeatures():
                memory_layer_data_provider.addFeature(feature)
            
            # add opis podloza fields
            self.__add_opis_podloza_fields(layer)
            
            # aggregate opis from gml
            opis_podloza_aggregates = self.__create_opis_podloza_aggregates(gml_path)
            
            plugin_dir = os.path.dirname(__file__)
            layer.loadNamedStyle(os.path.join(plugin_dir, "mapaGlebRolStyle", "kontur_glebowy_v3.qml"))
            layer.triggerRepaint()
            
            QgsProject.instance().addMapLayer(layer)
            return True
        except Exception as ex:
            QMessageBox.critical(None, "Błąd wczytywania", f"Nie udało się wczytać pliku gml: {ex}")
            print(f"Failed to load layer: {ex}")
            return False
        
    def __add_opis_podloza_fields(self, layer):
        layer.startEditing()
        for i in range(1,6):
            opis_podloza_etykieta = QgsField(f"opisPodloza{i}", QVariant.String)
            layer.dataProvider().addAttributes([opis_podloza_etykieta])
            layer.updateFields()
            
    def __create_opis_podloza_aggregates(self, gml_path):
        opis_podloza_aggregates = {}
        
        tree = ET.parse(gml_path)
        root = tree.getroot()
        
        namespaces = {
            'gml': 'http://www.opengis.net/gml/3.2',
            'gr': 'urn:gugik:specyfikacje:gmlas:mapaGlebowoRolnicza:1.0',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }

        for feature_member in root.findall('gml:featureMember', namespaces):
            for kontur_glebowy_node in feature_member.findall('gr:GR_KonturGlebowy', namespaces):
                lokalny_id = kontur_glebowy_node.find('gr:lokalnyId', namespaces).text
                opisy = {}
                item = 1
                for opis_podloza_node in kontur_glebowy_node.findall('gr:opisPodloza', namespaces):
                    numer_podloza = opis_podloza_node.find('gr:numerPodloza', namespaces).text
                    # podloze = opis_podloza_node.find('gr:podloze', namespaces).text
                    # szkieletowosc = opis_podloza_node.find('gr:szkieletowosc', namespaces).text
                    # rodzajGlebyOrganicznej = opis_podloza_node.find('gr:rodzajGlebyOrganicznej', namespaces).text
                    # miazszosc = opis_podloza_node.find('gr:miazszosc', namespaces).text
                    # gatunekRedziny = opis_podloza_node.find('gr:gatunekRedziny', namespaces).text
                    # informacjeDodatkowe = opis_podloza_node.find('gr:informacjeDodatkowe', namespaces).text
                    opisy[f"opisPodloza{item}"] = f"{numer_podloza} - podloze"
                    item = item + 1
                opis_podloza_aggregates[lokalny_id] = opisy
        print(opis_podloza_aggregates)
        return opis_podloza_aggregates