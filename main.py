import xml.etree.ElementTree as ET
from xml.dom import minidom
import json

# Парсим XML файл
tree = ET.parse('./input/test_input.xml')
root = tree.getroot()

# Словарь для новых XML объектов
new_xml_objects = {}

# Обработка объектов агрегации
for xml_aggregation_object in root.findall(".//Aggregation"):
    target_name = xml_aggregation_object.attrib['target']
    source_name = xml_aggregation_object.attrib['source']

    # Найти целевой и исходный XML классы (первый вызов для сохранения)
    target_xml = root.find(f".//Class[@name='{target_name}']")
    source_xml = root.find(f".//Class[@name='{source_name}']")

    # Создаем или получаем новые XML объекты
    target_xml_new = new_xml_objects.setdefault(target_name, ET.Element(target_name))
    source_xml_new = new_xml_objects.setdefault(source_name, ET.Element(source_name))

    # Добавляем исходный элемент в целевой
    target_xml_new.append(source_xml_new)

# Обработка классов и добавление атрибутов
for xml_class in root.findall(".//Class"):
    class_name = xml_class.attrib['name']
    class_new = new_xml_objects.get(class_name)

    if class_new is not None:
        for attr in xml_class:
            if attr.tag == 'Attribute':
                # Создаем элемент и присваиваем текст
                xml_attribute_element = ET.Element(attr.get('name'))
                xml_attribute_element.text = attr.get('type')
                class_new.insert(0, xml_attribute_element)  # Добавляем новый элемент

# Получение корневого XML объекта
root_xml_object = new_xml_objects[root.find(".//Class[@isRoot='true']").attrib['name']]

# Запись в новый XML файл
xml_str = ET.tostring(root_xml_object, encoding='utf-8', xml_declaration=True)
pretty_xml_as_string = minidom.parseString(xml_str).toprettyxml(indent="    ")

with open("output.xml", "w") as file:
    file.write(pretty_xml_as_string)


# ------------------------- JSON ---------------------------------
# Парсим XML файл
tree = ET.parse('./input/test_input.xml')
root = tree.getroot()


for xml_aggregation_object in root.findall(".//Aggregation"):
    target_name = xml_aggregation_object.attrib['target']
    source_name = xml_aggregation_object.attrib['source']

    target_xml = root.find(f".//Class[@name='{target_name}']")
    source_xml = root.find(f".//Class[@name='{source_name}']")

    source_xml.set('aggregation', xml_aggregation_object)

    target_xml.set(source_xml.attrib['name'], source_xml)

class_xml_tag_array = []
for xml_aggregation_object in root.findall(".//Class"):
    class_xml_tag_array.append(xml_aggregation_object.attrib['name'])


temp_orig_xml_object = []
for item in root.findall(".//Class"):
    temp_orig_xml_object.append(item)

for xml_item in temp_orig_xml_object:
    attributes = xml_item.findall("./Attribute")
    if len(attributes) != 0:
        xml_item.attrib['attributes'] = attributes

def xml_to_dict(element):
    """Преобразует XML элемент в словарь"""
    obj = {}

    obj[element.tag.lower()] = element.attrib['name']

    for attrib_item in element.attrib.items():
        if attrib_item[0] not in class_xml_tag_array and attrib_item[0] != 'name' and type(attrib_item[1]) == str:
            if attrib_item[1] == 'true':
                obj[attrib_item[0]] = True
            elif attrib_item[1] == 'false':
                obj[attrib_item[0]] = False
            else:
                obj[attrib_item[0]] = attrib_item[1]

    if element.attrib['isRoot'] != 'true':
        min_max = element.attrib['aggregation'].attrib['sourceMultiplicity'].split('..')
        obj["max"] = min_max[-1]
        obj["min"] = min_max[0]

    obj["parameters"] = []

    if 'attributes' in element.attrib.keys():
        for attribute in element.attrib['attributes']:
            temp_dict = {'name': attribute.attrib['name'], 'type': attribute.attrib['type']}
            obj["parameters"].append(temp_dict)

    for attrib_item in element.attrib.items():
        if attrib_item[0] in class_xml_tag_array:
            new_dict = {
                'name': attrib_item[0],
                'type': 'class'
            }

            obj["parameters"].append(new_dict)

    return obj


json_file = []
for xml_class in root.findall(".//Class"):
    json_file.append(xml_to_dict(xml_class))

data = json.dumps(json_file, indent=4)

with open('output.json', 'w') as file:
    file.write(data)


print(data)

