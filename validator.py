import xml.etree.ElementTree as ET
import datetime

from qgis.PyQt.QtWidgets import QMessageBox

class Validator:
    def validate_odkrywki(self, gml_path):
        required_nodes_main = ['gr:GR_OdkrywkaGlebowa']
        required_nodes_gr = {
            'gr:lokalnyId': {'type': 'string', 'required': True, 'nillable': False, 'nested': False},
            'gr:przestrzenNazw': {'type': 'string', 'required': True, 'nillable': False, 'nested': False},
            'gr:wersjaObiektu': {'type': 'date', 'required': True, 'nillable': False, 'nested': False},
            'gr:poczatekWersjiObiektu': {'type': 'date', 'required': True, 'nillable': False, 'nested': False},
            'gr:koniecWersjiObiektu': {'type': 'date', 'required': False, 'nillable': False, 'nested': False},
            'gr:dataUtworzenia': {'type': 'date', 'required': True, 'nillable': False, 'nested': False},
            'gr:numerOdkrywkiGlebowej': {'type': 'integer', 'required': True, 'nillable': False, 'nested': False},
            'gr:analiza': {'type': 'boolean', 'required': True, 'nillable': False, 'nested': False},
            'gr:URL': {'type': 'string', 'required': False, 'nillable': False, 'nested': False},
            'gr:uwagi': {'type': 'string', 'required': False, 'nillable': False, 'nested': False},
            'gr:aktualnosc': {'type': 'date', 'required': True, 'nillable': True, 'nested': False},
            'gr:uzytekGruntowy': {'type': 'string', 'required': True, 'nillable': True, 'nested': False},
            'gr:klasaBonitacyjna': {'type': 'string', 'required': True, 'nillable': True, 'nested': False},
            'gr:geometria': {'type': 'geometry', 'required': True, 'nillable': False, 'nested': True},
        }
        
        try:
            return self.__validate(gml_path, required_nodes_main, required_nodes_gr)

        except Exception as e:
            QMessageBox.critical(None, "Błąd Walidacji", f"Nie udało się otworzyć pliku gml: {e}")
            return False
    
    
    def validate_kontury(self, gml_path):
        required_nodes_main = ['gr:GR_KonturGlebowy']
        required_nodes_gr = {
            'gr:lokalnyId': {'type': 'string', 'required': True, 'nillable': False, 'nested': False},
            'gr:przestrzenNazw': {'type': 'string', 'required': True, 'nillable': False, 'nested': False},
            'gr:wersjaObiektu': {'type': 'date', 'required': True, 'nillable': False, 'nested': False},
            'gr:poczatekWersjiObiektu': {'type': 'date', 'required': True, 'nillable': False, 'nested': False},
            'gr:koniecWersjiObiektu': {'type': 'date', 'required': False, 'nillable': False, 'nested': False},
            'gr:dataUtworzenia': {'type': 'date', 'required': True, 'nillable': False, 'nested': False},
            'gr:opisPodloza': {'type': 'string', 'required': False, 'nillable': False, 'nested': True},
            'gr:skala': {'type': 'string', 'required': False, 'nillable': False, 'nested': False},
            'gr:skalaMacierzysta': {'type': 'string', 'required': False, 'nillable': False, 'nested': False},
            'gr:gatunekMady': {'type': 'string', 'required': False, 'nillable': False, 'nested': False},
            'gr:terenZalewowy': {'type': 'boolean', 'required': False, 'nillable': False, 'nested': False},
            'gr:uwagi': {'type': 'string', 'required': False, 'nillable': False, 'nested': False},
            'gr:zrodlo': {'type': 'string', 'required': True, 'nillable': False, 'nested': False},
            'gr:aktualnosc': {'type': 'date', 'required': True, 'nillable': True, 'nested': False},
            'gr:kompleks': {'type': 'string', 'required': True, 'nillable': True, 'nested': False},
            'gr:typPodtyp': {'type': 'string', 'required': True, 'nillable': True, 'nested': False},
            'gr:geometria': {'type': 'geometry', 'required': True, 'nillable': False, 'nested': True},
        }
        
        try:
            return self.__validate(gml_path, required_nodes_main, required_nodes_gr)

        except Exception as e:
            QMessageBox.critical(None, "Błąd Walidacji", f"Nie udało się otworzyć pliku gml: {e}")
            return False
    
    
    def __validate(self, gml_path, required_nodes_main, required_nodes_gr):
        tree = ET.parse(gml_path)
        root = tree.getroot()

        namespaces = {
            'gml': 'http://www.opengis.net/gml/3.2',
            'gr': 'urn:gugik:specyfikacje:gmlas:mapaGlebowoRolnicza:1.0',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }

        for feature_member in root.findall('gml:featureMember', namespaces):
            for main_node_name in required_nodes_main:
                if not self.__validate_main_node(feature_member, main_node_name, namespaces, required_nodes_gr):
                    return False
        return True

    def __validate_main_node(self, feature_member, main_node_name, namespaces, required_nodes_gr):
        main_node = feature_member.find(main_node_name, namespaces)        
        if main_node is None:
            QMessageBox.critical(None, "Błąd Walidacji", f"Wskazany plik gml nie zawiera wymaganych elementów: {main_node_name}")
            return False
        
        gml_id = main_node.attrib.get('{http://www.opengis.net/gml/3.2}id')
        if (gml_id is None or gml_id == ''):
            QMessageBox.critical(None, "Błąd Walidacji", f"Wskazany plik gml nie zawiera wymaganych atrybutu gml:id: {main_node_name}")
            return False
        self.gml_id = gml_id

        for gr_node, validation_rules in required_nodes_gr.items():
            if not self.__validate_gr_node(main_node, gr_node, namespaces, validation_rules):
                return False
        return True

    def __validate_gr_node(self, main_node, gr_node, namespaces, validation_rules):
        main_node_item = main_node.find(gr_node, namespaces)
        if main_node_item is None:
            if validation_rules['required']:
                QMessageBox.critical(None, "Błąd Walidacji", f"Wskazany plik gml nie zawiera wymaganych elementów: {gr_node}. gml:id: {self.gml_id}")
                return False
        else:
            if not validation_rules['nested']:
                val = main_node_item.text
                if val is None or val == '' and validation_rules['nillable']:
                    nil_val = main_node_item.attrib.get('nilReason')
                    if nil_val is None or nil_val == '':
                        print(f"NilReason: {nil_val}")
                        QMessageBox.critical(None, "Błąd Walidacji", f"Wskazany plik gml nie zawiera wymaganych elementów nilReason: {gr_node}. gml:id: {self.gml_id}")
                        return False
                if val is not None and len(val) > 0:
                    if not self.__validate_value(val, validation_rules, gr_node):
                        return False
        return True

    def __validate_value(self, val, validation_rules, gr_node):
        if validation_rules['type'] == 'integer':
            if not self.__integer_check(val):
                QMessageBox.critical(None, "Błąd Walidacji", f"Wartość elementu {gr_node} nie jest liczbą całkowitą: {val}. gml:id: {self.gml_id}")
                return False
        elif validation_rules['type'] == 'date':
            if not self.__date_check(val):
                QMessageBox.critical(None, "Błąd Walidacji", f"Wartość elementu {gr_node} nie jest datą: {val}. gml:id: {self.gml_id}")
                return False
        elif validation_rules['type'] == 'boolean':
            if not self.__boolean_check(val):
                QMessageBox.critical(None, "Błąd Walidacji", f"Wartość elementu {gr_node} nie jest wartością logiczną true/false: {val}. gml:id: {self.gml_id}")
                return False
        elif validation_rules['type'] == 'geometria':
            pass # for now passing
        return True
                            
    def __integer_check(self, val):
        try:
            int(val)
            return True
        except ValueError:
            return False
                            
    def __boolean_check(self, val):
        if val.lower() in ('true', 'false', '0', '1'):
            return True
        return False
    
    def __date_check(self, val):
        date_formats = [
        '%Y-%m-%d',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%dT%H:%M:%S',
        ]
        for date_format in date_formats:
            try:
                datetime.datetime.strptime(val, date_format)
                return True
            except ValueError:
                continue
        return False
