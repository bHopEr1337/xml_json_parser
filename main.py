import xml.etree.ElementTree as ET
from xml.dom import minidom
import json

tree = ET.parse('./input/test_input.xml')
""" Корень исходного файла """
root = tree.getroot()

origin_elements = []
elements_by_connection = {}
elements_with_attribute = {}

"""
Заполнение словаря элементами с атрибутами.
В результате:
{'class_name': {'name': 'type', 'name2': 'type'}}
"""
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

"""
Заполнение массива origin_elements именами классов xml.
В результате:
['имя_класса', 'имя_класса', .., 'имя_класса']
"""
for item in root:
    if item.tag == "Class":
        origin_elements.append(item.attrib['name'])

"""
Заполнение словаря именами классов. В качестве значения пустой словарь.
В результате:
elements_by_connection = {'имя_класса': {}, 'имя_класса':{}}
"""
for item in origin_elements:
    elements_by_connection[item] = {}

"""
Заполнение вложенных словарей у элементов словаря elements_by_connection.
Формирование связей между классами.
В результате:
elements_by_connection = {'имя_класса_1': {'имя_класса_2': 'имя_класса_2', 'имя_класса_3':'имя_класса_3'}, 'имя_класса4': {'имя_класса1': 'имя_класса1'}, ...}
"""
for item in root:
    if item.tag == "Aggregation":
        source = item.attrib['source']
        target = item.attrib['target']
        elements_by_connection[target][source] = source


"""
Фильтрация словаря elements_by_connection.
Удаляются элементы, у которых в значении пустой словарь,
иными словами удаляются тупиковые элементы, не имеющие 
дочерние элементы.
В результате:
elements_by_connection = {'имя_класса_1': {'имя_класса_2': 'имя_класса_2'}}
"""
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
    :param root: xml element корневой элемент.
    :return : String имя корневого тега.
    """
    for classElement in root.findall('Class'):
        if classElement.get('isRoot') == 'true':
            return classElement.attrib['name']

root_elem = search_root(root)


""" 
Создание нового XML корневого элемента для будущего output.xml
Элемент имеет имя существующего корневого элемента.
Словарь с атрибутами класса пустой.
"""
root_in_result_xml = ET.Element(root_elem)


""" Рекурсивная функция для добавления элементов """
def add_elements_recursively(parent_elem):
    """
    Функция ищет тэг корневого xml элемента в словаре связей. При нахождении, соответствующие элементы из
    этого словаря добавляются в качестве дочерних XML элементов в корень. Функция рекурсивно вызывается для
    раннее добавленных дочерних элементов, теперь они являются корневыми.
    :param parent_elem: дочерний XML элемент корня. Есть только тэг, атрибутов нет.
    :return : В результате первые дочерние XML элементы корня заполняются своими дочерними XML элементами.
    """
    if parent_elem.tag in elements_by_connection:
        for child_name in elements_by_connection[parent_elem.tag]:
            new_elem = ET.SubElement(parent_elem, child_name)
            add_elements_recursively(new_elem)


""" 
Находим тэги элементов, входящих в корнень и добавляем эти элементы XML в корень.
В результате корневой XML элемент приобретает SubElements 1 уровня вложенности.
"""
for item in elements_by_connection[root_in_result_xml.tag]:
    new_elem = ET.SubElement(root_in_result_xml, item)

""" 
Добавление дочерних XML элементов в XML элементы первого уровня вложенности.
root -> child1, child2, child3... -> new_child1_1, new_child1_2...
"""
for item in root_in_result_xml:
    add_elements_recursively(item)


""" Поиск элементов по имени """
def find_element_by_name(root, element_name):
    """
    Поиск в корне XML объекта по имени. Если имя искомого объекта совпадает с корнем,
    то возвращается корневой объект.
    :param root: XML корневой объект.
    :param element_name: string псевдоимя объекта, для которого нужно найти его реальный XML объект.
    :return root: XML корневой объект
    :return target_element: XML найденный по имени объект.
    """
    if element_name == root.tag:
        return root
    target_element = root.find(f".//{element_name}")
    # Вопрос, нужна ли тут проверка?
    if target_element != None:
        return target_element


""" Поиск XML объекта с атрибутами на основе словаря elements_with_attribute """
for name_of_xml_object in elements_with_attribute:
    xml_object_with_attributes = find_element_by_name(root_in_result_xml, name_of_xml_object)
    if xml_object_with_attributes != None:
        for name_attr, type_attr in elements_with_attribute[name_of_xml_object].items():
            new_sub_elem = ET.Element(name_attr)
            new_sub_elem.text = type_attr
            xml_object_with_attributes.insert(0, new_sub_elem)


new_tree = ET.ElementTree(root_in_result_xml)
xml_str = ET.tostring(root_in_result_xml, encoding='utf-8', xml_declaration=True)
pretty_xml_as_string = minidom.parseString(xml_str).toprettyxml(indent="    ")

with open("output.xml", "w") as file:
    file.write(pretty_xml_as_string)

# ------------------------- JSON ---------------------------------
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
