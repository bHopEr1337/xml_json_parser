import xml.etree.ElementTree as ET
from xml.dom import minidom
import json

tree = ET.parse('./input/test_input.xml')
""" Корень исходного файла """
root = tree.getroot()

origin_elements = []
elements_by_connection = {}
elements_with_attribute = {}

for class_elem in root.findall('Class'):
    attributes = class_elem.findall('Attribute')
    if len(attributes) != 0:
        for attr in attributes:
            key = class_elem.attrib['name']
            name = attr.attrib['name']
            type = attr.attrib['type']
            if key not in elements_with_attribute:
                elements_with_attribute[key] = {name: type}
            else:
                elements_with_attribute[key][name] = type

for item in root:
    if item.tag == "Class":
        origin_elements.append(item.attrib['name'])

for item in origin_elements:
    elements_by_connection[item] = {}

for item in root:
    if item.tag == "Aggregation":
        source = item.attrib['source']
        target = item.attrib['target']
        elements_by_connection[target][source] = source

keys_to_remove = []
for key, value in elements_by_connection.items():
    if len(value) == 0:
        keys_to_remove.append(key)

for key in keys_to_remove:
    elements_by_connection.pop(key)

""" Поиск корневого элемента """


def search_root(root):
    """
    Функция возвращает значение имени тега.
    Данное имя станет тегом будущего корня.
    """
    for classElement in root.findall('Class'):
        if classElement.get('isRoot') == 'true':
            return classElement.attrib['name']


root_elem = search_root(root)
""" Корень. В данном случае BTS """
root_in_result_xml = ET.Element(root_elem)

""" Рекурсивная функция для добавления элементов """


def add_elements_recursively(parent_elem, element_name):
    if element_name in elements_by_connection:
        for child_name in elements_by_connection[element_name]:
            new_elem = ET.SubElement(parent_elem, child_name)
            add_elements_recursively(new_elem, child_name)


for item in elements_by_connection[root_in_result_xml.tag]:
    new_elem = ET.SubElement(root_in_result_xml, item)

for item in root_in_result_xml:
    add_elements_recursively(item, item.tag)

""" Поиск элементов по имени """


def find_element_by_name(root, element_name):
    if element_name == root.tag:
        return root
    target_element = root.find(f".//{element_name}")
    if target_element != None:
        return target_element


for key, value in elements_with_attribute.items():
    target_elem = find_element_by_name(root_in_result_xml, key)
    if target_elem != None:
        for sub_key, sub_value in elements_with_attribute[key].items():
            new_sub_elem = ET.Element(sub_key)
            new_sub_elem.text = sub_value
            target_elem.insert(0, new_sub_elem)

new_tree = ET.ElementTree(root_in_result_xml)
xml_str = ET.tostring(root_in_result_xml, encoding='utf-8', xml_declaration=True)
pretty_xml_as_string = minidom.parseString(xml_str).toprettyxml(indent="    ")

with open("output.xml", "w") as file:
    file.write(pretty_xml_as_string)

# -----------------------------------------------------------
origin_elements2 = []
elements_by_connection = {}

for item in root:
    if item.tag == "Class":
        origin_elements2.append(item)

for item in origin_elements2:
    elements_by_connection[item] = {}


def search_class_by_aggregation(source, target):
    result_source = None
    result_target = None
    for origin_element in origin_elements2:
        if origin_element.attrib['name'] == source:
            result_source = origin_element
        if origin_element.attrib['name'] == target:
            result_target = origin_element
    if result_source != None and result_target != None:
        return (result_source, result_target)


""" ?Заполнение словаря? """
for item in root:
    if item.tag == "Aggregation":
        source = item.attrib['source']
        target = item.attrib['target']
        objects = search_class_by_aggregation(source, target)
        elements_by_connection[objects[1]][objects[0].attrib['name']] = objects[0]

element = origin_elements2[0]

""" Нужно создать словарь, у которого ключом будет название, а значением объект Aggregation """
elements_with_aggregation = {}
for elem in root.findall("Aggregation"):
    for origin_element in origin_elements:
        if origin_element == elem.attrib['source']:
            elements_with_aggregation[origin_element] = elem


def xml_to_dict(original_object):
    element_key = original_object
    result = {}

    """ Добавление атрибута "class" : "название класса" """
    result[element_key.tag.lower()] = element_key.attrib['name']
    for i in element_key.attrib:
        if i != 'name':
            if i == "isRoot":
                if element_key.attrib[i] == 'true':
                    result[i] = True
                else:
                    result[i] = False
            else:
                result[i] = element_key.attrib[i]

    if original_object.attrib['name'] != root_elem:
        number = elements_with_aggregation[original_object.attrib['name']].attrib['sourceMultiplicity']
        number = number.split("..")
        result['max'] = number[-1]
        result['min'] = number[0]

    result['parameters'] = [{}]

    """ Добавление вложенных классов в параметры "parameters": [{}] """
    i = 0
    for key, value in elements_by_connection[element_key].items():
        if i > 0:
            result['parameters'].append({})
        result['parameters'][i]['name'] = value.attrib['name']
        result['parameters'][i]['type'] = value.tag.lower()
        i += 1

    """ Добавление вложенных атрибутов <Attribute> """
    if element_key.attrib['name'] in elements_with_attribute:

        for item in elements_with_attribute[element_key.attrib['name']]:
            result['parameters'].append({})
            result['parameters'][i]['name'] = item
            result['parameters'][i]['type'] = elements_with_attribute[element_key.attrib['name']][item]
            i += 1

    if len(result['parameters'][-1]) == 0:
        result['parameters'].pop()

    return result


result_array = []
for elem in origin_elements2:
    xml_dict = xml_to_dict(elem)
    result_array.append(xml_dict)

json_data = json.dumps(result_array, ensure_ascii=False, indent=4)
with open("output.json", "w", encoding="utf-8") as json_file:
    json_file.write(json_data)

print(json_data)
