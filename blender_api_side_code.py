import bpy
import xml.etree.ElementTree as ET
from lxml import etree

# as lxml is not a part of blender python api library, need to install it using following code
"""
import subprocess
import sys
subprocess.call([sys.executable, "-m", "pip", "install", "lxml"])
"""


# simplyfying the name to make the mapping of assets easier
def get_asset_name(obj_name):
    for asset_name in asset_dict.keys():
        asset_name_no_spaces = asset_name.replace(' ', '').lower()
        if asset_name_no_spaces in obj_name.lower():
            return asset_name
    return None


slabcollection = bpy.context.scene.objects

# Load and parse the xsd schema
with open('\\baseline_xsd.xsd', 'rb') as f:
    xmlschema_doc = etree.parse(f)
    xmlschema = etree.XMLSchema(xmlschema_doc)

# Parse the xml document
with open('\\admm_xml.xml', 'rb') as f:
    tree = ET.parse(f)

# Convert to lxml element for validation *****
lxml_tree = etree.fromstring(ET.tostring(tree.getroot()))

# check if the provided xml for ITR conforms with schema
if not xmlschema.validate(lxml_tree):
    raise ValueError('xml document does not conform with the schema')

# use dicts to save all assets
root = tree.getroot()

asset_dict = {}
for asset_class in root.findall('AssetClass'):
    for asset_name in asset_class.findall('AssetName'):
        asset_dict[asset_name.attrib['name']] = asset_name

for obj in slabcollection:
    if obj.type == 'MESH':  # only considering meshes
        name = obj.name.split('/')[0]  # Assumes the name is in 'IfcSlab/Slab 1' format
        asset_name = get_asset_name(name)
        if asset_name is not None:
            # Apply attributes from the matching AssetName to the object.
            for attribute in asset_dict[asset_name].findall('Attribute'):
                # Get the name and format of the attribute
                attr_name = attribute.attrib['name']
                attr_format = attribute.attrib['format']
                attr_min_value = float(attribute.attrib.get('min_value', float('-inf')))
                attr_max_value = float(attribute.attrib.get('max_value', float('inf')))

                if attr_format == 'String':
                    obj[attr_name] = 'String'

                elif attr_format == 'Decimal':
                    attr_precision = int(attribute.attrib.get('precision', 2))
                    if attr_name.lower() == 'length':
                        obj[attr_name] = obj.scale.x
                    elif attr_name.lower() == 'width':
                        obj[attr_name] = obj.scale.y
                    else:
                        obj[attr_name] = 0.00

                    # Just to display the set limits from IR (Asset Information Requirements)
                    obj[attr_name + "_min"] = attr_min_value
                    obj[attr_name + "_max"] = attr_max_value
                    # print(attr_name)

                    # *** Following snippet sets the constraints 
                    # The soft limits need to be changed manually to experiment
                    prop = obj.id_properties_ui(attr_name)
                    prop.update(min=attr_min_value,
                                max=attr_max_value,
                                precision=attr_precision)

                    # Create a driver for the scale
                    if attr_name.lower() == 'length' or attr_name.lower() == 'width':
                        scale_axis = 'x' if attr_name.lower() == 'length' else 'y'
                        driver = obj.driver_add("scale", 'xyz'.index(scale_axis)).driver
                        driver.type = 'SCRIPTED'

                        var = driver.variables.new()
                        var.name = attr_name
                        var.type = 'SINGLE_PROP'
                        var.targets[0].id = obj
                        var.targets[0].data_path = '["{}"]'.format(attr_name)
                        driver.expression = var.name

                elif attr_format == 'Boolean':
                    obj[attr_name] = False

                elif attr_format == 'Date':
                    obj[attr_name] = 'Date'

                else:
                    obj[attr_name] = 'Unknown format'
