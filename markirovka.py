import csv
import itertools

def grouper(n, iterable):
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, n))
        if not chunk:
            return
        yield chunk


def markirovka(csv_file, field, privertka):

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

def main():

    # csv_file = '../data/190326_28349_2019-03_Франч с холдером_15 000.csv'
    csv_file = '../data/190326_28349_2019-03_Франч с холдером_15 000.csv'

    # номер поля из базы, считать с нуля
    field = 0

    # листов в привертке
    privertka = 500

    markirovka(csv_file, field, privertka)


if __name__ == '__main__':
    main()
