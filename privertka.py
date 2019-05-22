# -*- coding: utf-8 -*-

import csv
import pprint
import math
import chardet
from io import StringIO

pp = pprint.PrettyPrinter(indent=4)

"""
флаттен списка
>>> main_list = [[1,2,3],[4,5,6,7],[8,9]]
>>> [item for sublist in main_list for item in sublist]
[1, 2, 3, 4, 5, 6, 7, 8, 9]

"""


# deprecated
# def grouper(n, iterable):
#     it = iter(iterable)
#     while True:
#         chunk = tuple(itertools.islice(it, n))
#         if not chunk:
#             return
#         yield chunk


def privertka(csv_file, pile_size, places):
    """
    :param csv_file: входная база в формате csv, разделитель запятые
    :param pile_size: размер привертки в листах
    :param places: кол-во изделий на листе
    :return:

    Во второй части марлезонского балета (privertka2) я пытался представить выходную базу
    как двумерный массив, в котором строки - это печатные листы, а столбцы - это места для персухи.
    То есть так, как это выглядит в реальной выходной базе.
    Оказалось, что это ппц гемморой. Потому что чанки исходной базы нужно добавлять в новую каким-то
    через левое ухо способом.

    Пытаемся сделать, как было в первой версии, только со свежими мыслями.
    Теперь каждая строка - это изделие на листе:

    3 изделия на листе, всего листов 6:
    [[aa], [bb], [], [], [], []] - столбец персухи 1
    [[cc], [dd], [], [], [], []] - столбец персухи 2
    [[ee], [ff], [], [], [], []] - столбец персухи 3
      ^^
      изделие

     ^^^^^^^^^^^
      привертка

    """

    with open(csv_file, 'rb') as csv_bytes:
        rawdata = csv_bytes.read()
        charenc = chardet.detect(rawdata)['encoding']
        csv_string = StringIO(rawdata.decode(charenc))
        content = csv.reader(csv_string, delimiter=',')
        header = next(content, None)
        input_base = list(content)

    tiraz = len(input_base)
    print("Тираж: " + str(tiraz))
    print("На листе изделий: " + str(places))
    print("В привертке листов: " + str(pile_size))
    print("Полей персонализации:", len(header))

    izdeliy_v_privertke = pile_size * places
    print("В привертке изделий: " + str(izdeliy_v_privertke))

    full_pile_amount = tiraz//(pile_size * places)
    print("Кол-во целых приверток: " + str(full_pile_amount))

    print("Остаток изделий: " + str(tiraz % (pile_size * places)))


    # items - это список списков. Каждая строка - это "столбец" тиража в стопе, уже собранный по приверткам.
    # Содержит данные такого вида
    #
    # [['1', 'aaaaa', 'xx'], ['2', 'bbbbb', 'xx'], ['3', 'ccccc', 'xx'], ['4', 'ddddd', 'xx'], ['5', 'eeeee', 'xx'], ['11', 'mmmmm', 'xx'], ['12', 'gerf', 'xx'], ['13', 'flrg', 'xx'], ['14', 'erge', 'xx'], ['15', 'lkro', 'xx'], ['21', 'rger', 'xx'], ['22', 'ehth', 'xx'], ['23', 'kmik', 'xx'], ['24', 'ergb', 'xx'], ['25', 'ergk', 'xx']]
    # [['6', 'fffff', 'xx'], ['7', 'ggggg', 'xx'], ['8', 'iiiii', 'xx'], ['9', 'kkkkk', 'xx'], ['10', 'lllll', 'xx'], ['16', 'ergf', 'xx'], ['17', 'kiwu', 'xx'], ['18', 'erjg', 'xx'], ['19', 'hytj', 'xx'], ['20', 'utkj', 'xx'], ['26', 'egeg', 'xx'], ['27', 'ejer', 'xx'], ['28', 'gtrh', 'xx'], ['29', 'thrh', 'xx'], ['30', 'rhtr', 'xx']]
    items = []
    for i in range(places):
        h = [k+str(i+1) for k in header] # нумеруем заголовки (у нас же теперь несколько столбцов) - id1, id2....
        items.append([h])

    # Делаем сначала целые привертки (izdeliy_v_privertke)
    ostatok = input_base
    while len(ostatok) >= izdeliy_v_privertke:
        for i in range(places):
            chunk = ostatok[:pile_size]
            ostatok = ostatok[pile_size:]
            items[i] += chunk


    """
    DEPRECATED
    Этот кусок кода делит "хвост" на половинную привертку, потом еще раз на половинную,
    и так до тех пор, пока остаток не буедт меньше, чем очередная половина.
    Но, как я решил с манагерами, это будет только путать. 
    Поэтому хвост не делим, а просто раскладываем на одну привертку меньшей высоты. 
    half_size_privertka = math.floor(pile_size / 2)
    while len(ostatok) > half_size_privertka*places:

        print("Длина половины привертки", half_size_privertka)

        for i in range(places):
            chunk = ostatok[:half_size_privertka]
            ostatok = ostatok[half_size_privertka:]
            items[i] += chunk

        half_size_privertka = math.floor(half_size_privertka / 2)
    """


    # Раскладываем остаток на привертку меньшей высоты.
    # Если получаются пустые места, они расположены в один столбик в хвосте.
    print('------------------------------------- Хвост')
    hvost_izdeliy = len(ostatok)
    hvost_listov = math.ceil(hvost_izdeliy/places)
    print('hvost_listov', hvost_listov)
    dummy = places*hvost_listov - hvost_izdeliy
    print('Мест на листе', places, 'Листов в хвостике', hvost_listov)
    print(places, '*', hvost_listov, '=', places*hvost_listov)
    print('Пустых изделий добавить', dummy)

    # добавляем к остатку
    empty = ['' for i in range(len(header))]
    for i in range(dummy):
        ostatok.append(empty)

    print("ТЕПЕРЬ хвост составляет", len(ostatok))

    for i in range(places):
        chunk = ostatok[:hvost_listov]
        ostatok = ostatok[hvost_listov:]
        items[i] += chunk



    # печать результата
    # print()
    # for k, i in enumerate(items):
    #     print("Номер привертки:", k, "Длина привертки:", len(i))
    #     print(i)
    #     print('==============')


    print('----==============--------------=================-------------')

    # Транспонирование. Объеденяем сначала все первые записи (в строку), получаем первый лист, и т.д.
    # Результат сразу пишем в файл
    with open("csvoutput.csv", 'w', newline=r'\r\n') as f:
        for i in range(len(items[0])):
            z = []
            for j in range(places):
                z = z + items[j][i]
            # print(type(z))
            s = ','.join(z)
            f.write(s)

    # возвращаем:
    #  - тираж,
    #  - полей персонализации на изделии,
    #  - изделий в привертке
    #  - Кол-во целых приверток
    #  - изделий в хвосте
    #  - листов в хвосте
    #  - кол-во пустышек
    return tiraz, len(header), pile_size, izdeliy_v_privertke, full_pile_amount, hvost_izdeliy, hvost_listov, dummy


def main():

    # csv_file = '../data/190326_28349_2019-03_Франч с холдером_15 000.csv'
    # csv_file = '../data/MOCK_DATA.csv'
    csv_file = 'data/Job_Title.csv'

    # листов в привертке
    paper_pile_section = 2

    # изделий на листе
    places = 2

    privertka(csv_file, paper_pile_section, places)


if __name__ == '__main__':
    main()
