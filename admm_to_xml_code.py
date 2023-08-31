import csv
from xml.etree.ElementTree import Element, SubElement, ElementTree, tostring
from xml.dom import minidom


def prettify(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toxml()


root = Element('Assets')

with open('admm_sample_subset.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)

    current_class = None
    current_name = None
    class_elem = None
    name_elem = None

    for row in reader:
        asset_class, asset_name, _, attribute_name, _, attribute_status, attribute_format, _, attribute_measurement, _, attribute_precision, _, min_value, max_value = row[:14]

        if asset_class and asset_class != current_class:
            class_elem = SubElement(root, 'AssetClass')
            class_elem.set('name', asset_class)
            current_class = asset_class

        if asset_name and asset_name != current_name:
            name_elem = SubElement(class_elem, 'AssetName')
            name_elem.set('name', asset_name)
            current_name = asset_name

        attribute_elem = SubElement(name_elem, 'Attribute')
        attribute_elem.set('name', attribute_name)
        attribute_elem.set('status', attribute_status)
        attribute_elem.set('format', attribute_format)

        if attribute_measurement:
            attribute_elem.set('measurement', attribute_measurement)

        if min_value:
            attribute_elem.set('min_value', min_value)
        if max_value:
            attribute_elem.set('max_value', max_value)

        if attribute_precision:
            attribute_elem.set('precision', attribute_precision)

tree = ElementTree(root)
tree.write('admm_xml.xml', encoding='utf-8', xml_declaration=True)
