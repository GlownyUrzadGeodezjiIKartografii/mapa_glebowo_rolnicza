"""GML validation module"""

import xml.etree.ElementTree as ET
from lxml.etree import parse, XMLSchema
from qgis.PyQt.QtWidgets import QMessageBox
from .constants import FILE_ERROR_INFO, GML_NAMESPACES, VALIDATION_ERROR_INFO

class ValidationService:
    """GML validation service"""

    def validate_kontury_with_schema(self, gml_path, schema_path, progressBarControle):
        """Method to validate kontury gml and gml file with schema"""

        try:
            schema_result, validation_errors = self.__validate_with_schema(gml_path, schema_path, progressBarControle)

            tree = ET.parse(gml_path)
            root = tree.getroot()
            kontury_exists = False
            for feature_member in root.findall('gml:featureMember', GML_NAMESPACES):
                for _ in feature_member.findall('gr:GR_KonturGlebowy', GML_NAMESPACES):
                    kontury_exists = True
                    break
            if not kontury_exists:
                validation_errors['nie dotyczy'] = 'Brak konturów glebowych [gr:GR_KonturGlebowy] w pliku gml'
                QMessageBox.critical(None, FILE_ERROR_INFO, f"Brak konturów glebowych [gr:GR_KonturGlebowy] w pliku gml")
            if len(validation_errors) > 0:
                return False, validation_errors
            if not schema_result:
                return False, None
            return True, None
        except Exception as e:
            QMessageBox.critical(None, VALIDATION_ERROR_INFO, f"Nie udało się otworzyć pliku gml")
            print(e)
            return False, None

    def validate_odkrywki_with_schema(self, gml_path, schema_path, progressBarControle):
        """Method to validate odkrywki gml and gml file with schema"""

        try:
            schema_result, validation_errors = self.__validate_with_schema(gml_path, schema_path, progressBarControle)

            tree = ET.parse(gml_path)
            root = tree.getroot()
            odkrywki_exists = False
            for feature_member in root.findall('gml:featureMember', GML_NAMESPACES):
                for _ in feature_member.findall('gr:GR_OdkrywkaGlebowa', GML_NAMESPACES):
                    odkrywki_exists = True
                    break
            if not odkrywki_exists:
                validation_errors['nie dotyczy'] = 'Brak okrywek glebowych [gr:GR_OdkrywkaGlebowa] w pliku gml'            
                QMessageBox.critical(None, FILE_ERROR_INFO, f"Brak okrywek glebowych [gr:GR_OdkrywkaGlebowa] w pliku gml")
            if len(validation_errors) > 0:
                return False, validation_errors
            if not schema_result:
                return False, None
            return True, None
        except Exception as e:
            QMessageBox.critical(None, VALIDATION_ERROR_INFO, f"Nie udało się otworzyć pliku gml")
            print(e)
            return False, None

    def __validate_with_schema(self, gml_path, schema_path, progressBarControle):
        """Method to validate gml file with schema"""

        xmlschema = XMLSchema(parse(schema_path))
        gmlFile = parse(gml_path)
        validation_errors = {}
        if gmlFile.getroot() is not None:
            items_to_validation = list(gmlFile.iter())
            progressBarControle.setMaximum(len(items_to_validation))
            for element in items_to_validation:
                progressBarControle.setValue(progressBarControle.value() + 1)
                if str(element.tag).endswith('featureMember'):
                    validationResult = xmlschema.validate(element)
                    if not validationResult:
                        for subelement in element:
                            validation_errors[f"{subelement.attrib['{http://www.opengis.net/gml/3.2}id']}"] = xmlschema.error_log

        if len(validation_errors) > 0:
            QMessageBox.critical(None, VALIDATION_ERROR_INFO, f"Wskazany plik gml nie waliduje się. Znalezione błędy: {len(validation_errors)}")
            return False, validation_errors

        return True, {}

    def save_errors_to_file(self, errors, file_path):
        """Save the validation errors to a text file."""

        with open(file_path, 'w') as file:
            for key, value in errors.items():
                file.write(f"gml Id: {key} : {value}\n\n")
