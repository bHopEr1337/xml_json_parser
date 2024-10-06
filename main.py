import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

from typing import Dict, List
from xml.dom import minidom
import json


class XMLParser:
    """Класс XMLParser используется для формирования xml файла с иерархией

    Основное применение - создание файла config.xml. Данный файл представляет собой пример внутренней
    конфигурации базовой станции, соответствующий представленной модели.

    Note:
        Результирующий файл не содержит атрибуты xml объектов. В файле отражаются
        только сами объекты и их дочерние элементы "Class или Attribute"

    Attributes
    ----------
    __input_file_name : str
        название исходного файла. Например: 'test_input.xml'

    Methods
    -------
    main()
        Запускает парсер, который создаёт файл config.xml с иерархией. Данный файл находится
        в директории 'out', которая находится на одном уровне с 'main.py'.
    """

    def __init__(self, input_file_name: str):
        self.__input_file_name = input_file_name
        self.__tree = ET.parse(f'./input/{self.__input_file_name}')
        self.__root = self.__tree.getroot()

    def __add_child_to_parent_xml(self) -> Dict[str, Element]:
        """Создание новых xml объектов Class на основе существующих и
        добавление в них дочерних xml объектов, которые никаких ат-
        рибутов не имеют.

        Note:
            Формирование словаря xml объектов:
            empty_xml_objects = {'class_name': <xml class_name object>, ...}
            Каждый объект в этом словаре хранит внутри себя дочерние xml объекты,
            если такие имеются.

        return
        ------
        empty_xml_objects : Dict
            Словарь, хранящий xml объекты Class по их названию. Внутри каждого
            такого объекта находятся дочерние элементы.
        """
        empty_xml_objects: Dict[str, Element] = {}

        # В xml объектах Aggregation получаем имена объектов source и target.
        for xml_aggregation_object in self.__root.findall(".//Aggregation"):
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


    def __add_attribute_to_xml(self, empty_xml_objects: Dict[str, Element]) -> None:
        """Добавляет элементы Attribute из исходного XML объекта Class (xml_real_class)
        в соответствующий пустой XML объект Class (empty_xml_class).

        Эта функция проходит по всем классам в исходном XML и для каждого класса
        ищет соответствующий пустой объект. Если такой объект существует,
        в него добавляются дочерние элементы атрибутов.

        :param empty_xml_objects: Dict[str, Element]
            Словарь, содержащий пустые XML объекты Class,
            где ключом является имя класса, а значением — элемент XML.

        :return: None
            Функция не возвращает значений; она модифицирует
            существующие XML объекты, добавляя атрибуты.

        Note:
            Например, атрибуты с именами и типами, извлечённые из
            исходного класса, будут добавлены как дочерние элементы в
            соответствующий пустой XML класс.
        """

        # Обработка классов и добавление атрибутов
        for xml_real_class in self.__root.findall(".//Class"):
            name_of_xml_real_class = xml_real_class.attrib['name']
            empty_xml_class = empty_xml_objects.get(name_of_xml_real_class)

            if empty_xml_class is not None:
                for xml_real_attribute in xml_real_class.findall('Attribute'):
                    # Создаем элемент и присваиваем текст
                    xml_attribute_element = ET.Element(xml_real_attribute.get('name'))
                    xml_attribute_element.text = xml_real_attribute.get('type')
                    empty_xml_class.insert(0, xml_attribute_element)


    def __get_root_xml(self, empty_xml_objects: Dict[str, Element]) -> Element:
        """Находит корневой XML объект из словаря пустых XML объектов,
        который был получен в результате работы функции
        `add_child_to_parent_xml()`.

        Эта функция ищет класс с атрибутом `isRoot`, который
        указывает на то, что данный класс является корнем,
        и возвращает соответствующий XML объект из словаря.

        :param empty_xml_objects: Dict[str, Element]
            Словарь, содержащий пустые XML объекты,
            где ключом является имя класса, а значением — элемент XML.

        :return: Element
            Корневой XML объект, соответствующий классу с атрибутом
            `isRoot='true'` из словаря `empty_xml_objects`.

        Note:
            Если корневой класс не найден, может возникнуть исключение
            KeyError. Рекомендуется предварительно проверить наличие
            класса с `isRoot='true'` в XML перед вызовом этой функции.
        """

        root_xml_object = empty_xml_objects[self.__root.find(".//Class[@isRoot='true']").attrib['name']]
        return root_xml_object

    def __make_file_from_xml(self, root_xml_object: Element) -> None:
        """Создает XML файл из переданного корневого XML объекта.

        Функция преобразует объект типа `Element` в строку формата XML и
        записывает его в файл с именем "output.xml" в удобочитаемом формате.

        :param root_xml_object: Element
            Корневой объект XML, который будет преобразован в строку
            и сохранен в файл.

        :return: None
            Функция не возвращает значений; результат сохраняется напрямую
            в файл "output.xml".

        Note:
            При каждом вызове этой функции содержимое файла "output.xml"
            будет перезаписано. Убедитесь, что данные, которые вы хотите
            сохранить, не потеряются.
        """

        xml_str = ET.tostring(root_xml_object, encoding='utf-8', xml_declaration=True)
        pretty_xml_as_string = minidom.parseString(xml_str).toprettyxml(indent="    ")

        with open("output.xml", "w") as file:
            file.write(pretty_xml_as_string)


    def __start_xml_parser(self):
        empty_xml_objects = self.__add_child_to_parent_xml()
        self.__add_attribute_to_xml(empty_xml_objects)
        root_xml_object = self.__get_root_xml(empty_xml_objects)
        self.__make_file_from_xml(root_xml_object)

    def main(self):
        """Запуск парсера"""

        self.__start_xml_parser()


# ------------------------- JSON ---------------------------------


class JSONParser:
    """Класс JSONParser используется для формирования json файла

    Основное применение - создание файла meta.json. Данный файл содержит мета-информацию
    о классах и их атрибутах. Фронтенд использует данный файл для корректного отображения
    дерева объектов в интерфейсе пользователя (UI).

    Note:
        В данном файле в json формате отображена вся информация о каждом xml объекте Class:
        атрибуты, вложенные классы, метрики.

    Attributes
    ----------
    __input_file_name : str
        название исходного файла. Например: 'test_input.xml'

    Methods
    -------
    main()
        Запускает парсер, который создаёт файл meta.json. Данный файл находится
        в директории 'out', которая находится на одном уровне с 'main.py'.
    """

    def __init__(self, input_file):
        self.__input_file = input_file
        self.__tree = ET.parse(f'./input/{self.__input_file}')
        self.__root = self.__tree.getroot()

    def __add_to_xml_child_and_aggregation(self) -> None:
        """Добавляет новые атрибуты в исходные XML объекты Class, включая
        дочерние объекты и объекты связи Aggregation.

        Функция находит все объекты Aggregation в исходном XML и
        устанавливает два типа атрибутов для целевых и исходных классов:
        1. Дочерние XML объекты Class, добавляемые к атрибутам `target`.
        2. Объект связи Aggregation, устанавливаемый для `source`.

        :return: None
            Функция не возвращает значений и модифицирует существующие
            XML объекты напрямую.
        """

        for xml_aggregation_object in self.__root.findall(".//Aggregation"):
            target_name: str = xml_aggregation_object.attrib['target']
            source_name: str = xml_aggregation_object.attrib['source']

            target_xml: Element = self.__root.find(f".//Class[@name='{target_name}']")
            source_xml: Element = self.__root.find(f".//Class[@name='{source_name}']")

            # Добавление дочернего xml объекта Attribute в качестве атрибута.
            source_xml.set('aggregation', xml_aggregation_object)

            # Добавление дочернего xml объекта Class в качестве атрибута.
            target_xml.set(source_xml.attrib['name'], source_xml)

    def __make_class_xml_tag_array(self) -> List[str]:
        """Ищет объекты Class в корневом элементе XML и формирует список
        их имен.

        Функция проходит по всем найденным объектам Class и собирает
        их имена в список `class_xml_tag_array`, который затем возвращается.

        :return class_xml_tag_array: List[str]
            Список строк, содержащий имена XML объектов Class, найденных в корне.
        """

        class_xml_tag_array: List[str] = []
        for xml_aggregation_object in self.__root.findall(".//Class"):
            class_xml_tag_array.append(xml_aggregation_object.attrib['name'])

        return class_xml_tag_array

    def __make_list_with_xml_class(self) -> List[Element]:
        """Ищет и собирает объекты Class из корневого элемента XML в список.

        Функция проходит по всем найденным объектам Class и добавляет
        их в список `temp_orig_xml_object`, который затем возвращается.

        :return temp_orig_xml_object: List[Element]
            Список объектов типа Element, представляющих XML объекты Class,
            найденные в корне.
        """

        temp_orig_xml_object: List[Element] = []
        for item in self.__root.findall(".//Class"):
            temp_orig_xml_object.append(item)

        return temp_orig_xml_object

    def __add_xml_attribute_to_xml(self, temp_orig_xml_object: List[Element]) -> None:
        """Получает вложенные XML объекты Attribute и добавляет их в родительский
        объект Class в качестве атрибута 'attributes'.

        Функция проходит по всем переданным объектам Class и ищет их
        вложенные объекты Attribute. Если они найдены, объекты добавляются
        в качестве атрибута 'attributes' родительского элемента.

        :param temp_orig_xml_object: List[Element]
            Список объектов XML Class, в которых нужно искать вложенные
            объекты Attribute.
        """

        for xml_item in temp_orig_xml_object:
            attributes = xml_item.findall("./Attribute")
            if len(attributes) != 0:
                xml_item.attrib['attributes'] = attributes

    def __str_to_bool(self, string):
        """Преобразует строковое представление булевого значения в тип

        :param string: str
            Строковое значение, которое необходимо преобразовать.

        :return: bool or str
            Возвращает True, False или исходную строку, если
            строка не соответствует 'true' или 'false'.
        """

        if string == 'true':
            return True
        elif string == 'false':
            return False
        return string

    def __xml_to_dict(self, element: Element, class_xml_tag_array: List[str]) -> Dict:
        """Преобразует XML объект Class в словарь.

        Функция принимает элемент XML и преобразует его в словарь,
        извлекая атрибуты и вложенные объекты.

        :param element: Element
            XML объект Class, который нужно сериализовать.

        :param class_xml_tag_array: List[str]
            Список с именами XML объектов Class, чтобы фильтровать атрибуты.

        :return: Dict
            Словарь, представляющий сериализованные XML объекты.
        """

        obj = {}

        # Добавление имени элемента в словарь
        obj[element.tag.lower()] = element.attrib['name']

        # Добавление атрибутов в словарь
        for attrib_item in element.attrib.items():
            if attrib_item[0] not in class_xml_tag_array and attrib_item[0] != 'name' and type(attrib_item[1]) == str:
                obj[attrib_item[0]] = self.__str_to_bool(attrib_item[1])

        # Добавление метрики
        if element.attrib['isRoot'] != 'true':
            min_max = element.attrib['aggregation'].attrib['sourceMultiplicity'].split('..')
            obj["max"] = min_max[-1]
            obj["min"] = min_max[0]

        obj["parameters"] = []

        # Обработка вложенных атрибутов XML
        if 'attributes' in element.attrib.keys():
            for attribute in element.attrib['attributes']:
                temp_dict = {'name': attribute.attrib['name'], 'type': attribute.attrib['type']}
                obj["parameters"].append(temp_dict)

        # Обработка вложенных объектов Class
        for attrib_item in element.attrib.items():
            if attrib_item[0] in class_xml_tag_array:
                new_dict = {
                    'name': attrib_item[0],
                    'type': 'class'
                }
                obj["parameters"].append(new_dict)

        return obj

    def __make_file_from_json(self, class_xml_tag_array: List[str]):
        """Создаёт JSON файл из объектов XML Class.

        Функция итерирует по всем объектам Class в корневом элементе XML,
        преобразует каждый объект в словарь с помощью метода __xml_to_dict,
        а затем сохраняет полученные данные в файл output.json.

        :param class_xml_tag_array: List[str]
            Список с именами XML объектов Class, используемый для фильтрации атрибутов.

        :return: None
        """

        json_file = []
        for xml_class in self.__root.findall(".//Class"):
            json_file.append(self.__xml_to_dict(xml_class, class_xml_tag_array))

        data = json.dumps(json_file, indent=4)

        with open('output.json', 'w') as file:
            file.write(data)

    def __start_json_parser(self):
        self.__add_to_xml_child_and_aggregation()
        class_xml_tag_array = self.__make_class_xml_tag_array()
        temp_orig_xml_object = self.__make_list_with_xml_class()
        self.__add_xml_attribute_to_xml(temp_orig_xml_object)
        self.__make_file_from_json(class_xml_tag_array)

    def main(self):
        """Запуск парсера"""

        self.__start_json_parser()


if __name__ == '__main__':
    obj_xml = XMLParser('test_input.xml')
    obj_xml.main()

    obj_json = JSONParser('test_input.xml')
    obj_json.main()