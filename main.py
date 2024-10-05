import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

from typing import Dict
from xml.dom import minidom
import json


def add_child_to_parent_xml(root: Element) -> Dict[str, Element]:
    """
    Создание новых xml объектов Class на основе существующих и
    добавление в них дочерних xml объектов, которые никаких ат-
    рибутов не имеют. Формирование словаря xml объектов:
    empty_xml_objects = {'class_name': <xml class_name object>, ...}
    Каждый объект в этом словаре хранит внутри себя дочерние xml объекты,
    если такие имеются.
    :param root: Element - корень исходной структуры.
    :return: Dict empty_xml_objects - словарь, хранящий xml объекты Class по их
    названию. Внутри каждого такого объекта находятся дочерние элементы.
    """
    empty_xml_objects: Dict[str, Element] = {}

    # В xml объектах Aggregation получаем имена объектов source и target.
    for xml_aggregation_object in root.findall(".//Aggregation"):
        target_name = xml_aggregation_object.attrib['target']
        source_name = xml_aggregation_object.attrib['source']

        # Создаем или получаем новые XML объекты.
        # Если в словаре уже есть такой ключ, то возвращаем существующее значение (xml объект).
        # Если в словаре нет такого ключа, добавляем новую пару в словарь и возвращаем новое значение (xml объект).
        target_xml_new: Element = empty_xml_objects.setdefault(target_name, ET.Element(target_name))
        source_xml_new: Element = empty_xml_objects.setdefault(source_name, ET.Element(source_name))

        # Добавляем исходный элемент в целевой
        target_xml_new.append(source_xml_new)

    return empty_xml_objects


def add_attribute_to_xml(root: Element, empty_xml_objects: Dict[str, Element]) -> None:
    """
    Функция соотносит скопированный пустой xml объект Class (empty_xml_class)
    с исходным xml объектом Class (xml_real_class).
    Из исходного объекта в скопированный объект добавляются дочерние xml объекты Attribute.
    :param root: Element - корень исходной структуры.
    :param empty_xml_objects: Dict[str, Element] - словарь, содержащий пустые xml объекты.
    :return: None
    """
    # Обработка классов и добавление атрибутов
    for xml_real_class in root.findall(".//Class"):
        name_of_xml_real_class = xml_real_class.attrib['name']
        empty_xml_class = empty_xml_objects.get(name_of_xml_real_class)

        for xml_real_attribute in xml_real_class.findall('Attribute'):
            # Создаем элемент и присваиваем текст
            xml_attribute_element = ET.Element(xml_real_attribute.get('name'))
            xml_attribute_element.text = xml_real_attribute.get('type')
            empty_xml_class.insert(0, xml_attribute_element)


def get_root_xml(empty_xml_objects: Dict[str, Element], root: Element) -> Element:
    """
    Поиск корневого xml объекта из словаря, который был получен в результате работы
    функции add_child_to_parent_xml()
    :param empty_xml_objects: Dict[str, Element] - словарь, содержащий пустые xml объекты.
    :param root: Element - корень исходной структуры.
    :return root_xml_object: Element корневой xml объект из словаря.
    """
    root_xml_object = empty_xml_objects[root.find(".//Class[@isRoot='true']").attrib['name']]
    return root_xml_object


def make_file_from_xml(root_xml_object: Element) -> None:
    """
    Создает XML файл из переданного корневого XML объекта.
    Функция преобразует объект типа Element в строку формата XML и
    записывает его в файл с именем "output.xml" в удобочитаемом формате.
    :param root_xml_object: Element - корневой объект XML, который будет
    преобразован в строку и сохранен в файл.
    :return: None - функция не возвращает ничего и выполняет запись
    непосредственно в файл.
    """
    xml_str = ET.tostring(root_xml_object, encoding='utf-8', xml_declaration=True)
    pretty_xml_as_string = minidom.parseString(xml_str).toprettyxml(indent="    ")

    with open("output.xml", "w") as file:
        file.write(pretty_xml_as_string)


def main():
    tree = ET.parse('./input/test_input.xml')
    root = tree.getroot()
    empty_xml_objects = add_child_to_parent_xml(root)
    add_attribute_to_xml(root, empty_xml_objects)
    root_xml_object = get_root_xml(empty_xml_objects, root)
    make_file_from_xml(root_xml_object)


if __name__ == '__main__':
    main()


# ------------------------- JSON ---------------------------------
# for xml_aggregation_object in root.findall(".//Aggregation"):
#     target_name = xml_aggregation_object.attrib['target']
#     source_name = xml_aggregation_object.attrib['source']
#
#     target_xml = root.find(f".//Class[@name='{target_name}']")
#     source_xml = root.find(f".//Class[@name='{source_name}']")
#
#     source_xml.set('aggregation', xml_aggregation_object)
#
#     target_xml.set(source_xml.attrib['name'], source_xml)
#
# class_xml_tag_array = []
# for xml_aggregation_object in root.findall(".//Class"):
#     class_xml_tag_array.append(xml_aggregation_object.attrib['name'])
#
#
# temp_orig_xml_object = []
# for item in root.findall(".//Class"):
#     temp_orig_xml_object.append(item)
#
# for xml_item in temp_orig_xml_object:
#     attributes = xml_item.findall("./Attribute")
#     if len(attributes) != 0:
#         xml_item.attrib['attributes'] = attributes
#
#
# def str_to_bool(string):
#     if string == 'true':
#         return True
#     elif string == 'false':
#         return False
#     else:
#         return string
#
# def xml_to_dict(element):
#     """Преобразует XML элемент в словарь"""
#     obj = {}
#
#     obj[element.tag.lower()] = element.attrib['name']
#
#     for attrib_item in element.attrib.items():
#         if attrib_item[0] not in class_xml_tag_array and attrib_item[0] != 'name' and type(attrib_item[1]) == str:
#             obj[attrib_item[0]] = str_to_bool(attrib_item[1])
#
#     if element.attrib['isRoot'] != 'true':
#         min_max = element.attrib['aggregation'].attrib['sourceMultiplicity'].split('..')
#         obj["max"] = min_max[-1]
#         obj["min"] = min_max[0]
#
#     obj["parameters"] = []
#
#     if 'attributes' in element.attrib.keys():
#         for attribute in element.attrib['attributes']:
#             temp_dict = {'name': attribute.attrib['name'], 'type': attribute.attrib['type']}
#             obj["parameters"].append(temp_dict)
#
#     for attrib_item in element.attrib.items():
#         if attrib_item[0] in class_xml_tag_array:
#             new_dict = {
#                 'name': attrib_item[0],
#                 'type': 'class'
#             }
#             obj["parameters"].append(new_dict)
#
#     return obj
#
#
# json_file = []
# for xml_class in root.findall(".//Class"):
#     json_file.append(xml_to_dict(xml_class))
#
# data = json.dumps(json_file, indent=4)
#
# with open('output.json', 'w') as file:
#     file.write(data)
#
#
# print(data)

