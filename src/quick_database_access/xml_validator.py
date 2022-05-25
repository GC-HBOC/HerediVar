from lxml import etree, objectify
from io import StringIO

class xml_validator:

    def __init__(self, xsd_path: str):
        xmlschema_doc = etree.parse(xsd_path)
        self.xmlschema = etree.XMLSchema(xmlschema_doc)

    def validate(self, xml: str) -> bool:
        if xml.startswith('<'):
            xml = StringIO(xml)
        xml_doc = etree.parse(xml)
        result = self.xmlschema.validate(xml_doc)
        return result
    
    def object_from_string_validate(self, xml: str) -> bool:
        parser = objectify.makeparser(schema = self.xmlschema)
        result = objectify.fromstring(xml, parser)
        return result

    def object_from_string(self, xml: str) -> bool:
        return objectify.fromstring(xml)
