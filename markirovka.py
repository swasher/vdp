import csv
import itertools
import math
from flask import session


def grouper(n, iterable):
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, n))
        if not chunk:
            return
        yield chunk


# DEPRECATED
def markirovka1(csv_file, field, privertka):

    with open(csv_file, newline='') as csvfile:
        content = csv.reader(csvfile, delimiter=',')
        next(content, None)

        out_file_name = csv_file+'_PRIV_'+str(privertka)+'.csv'

        with open(out_file_name, mode='w', newline='') as outfile:

            w = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            g = grouper(privertka, content)

            pachka_number = 0

            for l in g:
                pachka_number +=1
                pachka_size = len(l)
                diapazon = l[0][field]+' - '+l[-1][field]

                w.writerow([diapazon, pachka_size, pachka_number])
                #print(s, end="\r") #печать в консоль в одну строку, типа прогресс

# todo маркировка столбцов

def do_perekladka(csv_file, out_file):
    """
    Перекладку формируем исходя из размера привертки (pile_size)
    За основу берем код privertka.py и модифицируем

    Нам нужны такие столбцы
      - номер заказа
      - номер привертки
      - номер пачки и кол-во пачек (5 из 50)
      - кол-во изделий в пачке
      - DEPRECATED номера изделий (напр., всего 10 000 изделий, на пачке может быть написано 5501-6000)
      - персонализация с - по (т.е. переменное на первом изделии в пачке - тире - последнее в пачке)

    :param csv_file:
    :param pile_size:
    :param places:
    :param input_encoding:
    :return:
    """

    # номер колонки для печати на перекладке (первая - ноль)
    colon = 0

    order = session['order']
    places = session['places']
    pile_size = session['pile']
    input_encoding = session['input_encoding']
    izdeliy_v_privertke = pile_size * places

    fieldnames = ['order', 'privertka', 'pachka', 'amount', 'pers']

    pachka = 0
    privertka = 0

    with open(csv_file, 'r', encoding=input_encoding) as csv_string:
        content = csv.reader(csv_string, delimiter=',')
        header = next(content, None)
        input_base = list(content)

    tiraz = len(input_base)
    full_pile_amount = tiraz // (pile_size * places)
    kolich_pachkek_bez_hvosta = full_pile_amount * places
    # количество пачек в хвосте всегда равно places
    total_pachki = kolich_pachkek_bez_hvosta + places

    with open(out_file, 'w', newline='\r\n') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Делаем сначала целые привертки (izdeliy_v_privertke)
        ostatok = input_base
        while len(ostatok) >= izdeliy_v_privertke:
            privertka += 1
            for i in range(places):
                chunk = ostatok[:pile_size]
                pers = ' - '.join([chunk[0][colon], chunk[-1][colon]])
                amount = len(chunk)
                ostatok = ostatok[pile_size:]
                pachka += 1

                # writer.writerow({'order': order, 'privertka': privertka, 'pachka': pachka, 'amount': amount, 'pers': pers})
                writer.writerow({'order': f'№ Заказа: {order}',
                                 'privertka': f'Привертка № {privertka}',
                                 'pachka': f'Пачка №{pachka} (из {total_pachki})',
                                 'amount': f'Кол-во в пачке: {amount}',
                                 'pers': f'Номера с/по: {pers}'})

                # str = f'Заказ: {order}\nПривертка {privertka}\nПачка: {pachka}\nВ пачке: {amount}\nНомера {pers}'
                # csvfile.write(str)

        # а теперь хвост (хвост, это когда изделий уже не хватает на целую привертку)
        hvost_izdeliy = len(ostatok)
        hvost_listov = math.ceil(hvost_izdeliy / places)
        dummy = places * hvost_listov - hvost_izdeliy

        # добавляем к остатку
        empty = ['-' for i in range(len(header))]
        for i in range(dummy):
            ostatok.append(empty)

        privertka += 1
        for i in range(places):
            chunk = ostatok[:hvost_listov]

            pachka += 1
            pers = ' - '.join([chunk[0][colon], chunk[-1][colon]])
            ostatok = ostatok[hvost_listov:]
            amount = len(chunk)

            # отнимаем из количества изделий в последней пачке кол-во пустышек
            if i == places-1:
                amount -= dummy

            writer.writerow({'order': f'№ Заказа: {order}',
                             'privertka': f'Привертка № {privertka}',
                             'pachka': f'Пачка №{pachka} (из {total_pachki})',
                             'amount': f'Кол-во в пачке: {amount}',
                             'pers': f'Номера с/по: {pers}'})
            # str = f'Заказ: {order}\nПривертка {privertka}\nПачка: {pachka}\nВ пачке: {amount}\nНомера {pers}'
            # csvfile.write(str)


def main():

    # csv_file = '../data/190326_28349_2019-03_Франч с холдером_15 000.csv'
    csv_file = '../data/190326_28349_2019-03_Франч с холдером_15 000.csv'

    # номер поля из базы, считать с нуля
    field = 0

    # листов в привертке
    privertka = 500

    markirovka1(csv_file, field, privertka)


if __name__ == '__main__':
    main()
