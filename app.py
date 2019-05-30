import os
import re
import csv
from flask import Flask
from flask import session
from flask import send_file
from flask import request
from flask import render_template
from werkzeug.utils import secure_filename


from privertka import privertka
from markirovka import perekladka
from util import read_n_lines
from util import allowed_file

app = Flask(__name__)
N = int(os.getenv("N"))
app.secret_key = os.getenv("SECRET_KEY")


@app.route('/', methods=["GET", "POST"])
def main():
    n = N
    input_file = "csvinput.csv"
    converted_file = "csvoutput.csv"
    if request.method == "POST":
        if 'csvinput' in request.files:
            f = request.files['csvinput']
            if f and allowed_file(f.filename):
                # filename = secure_filename(file.filename)
                f.save(input_file)

            csv_input, input_encoding = read_n_lines(input_file, n)
            filename = secure_filename(f.filename)

            pattern = r'\d\d-\d\d\d\d'
            result = re.match(pattern, filename)
            order = result.group(0) if result else None

            tiraz, perso_mest, bad_data, trouble = consistency(input_file, input_encoding)
            if bad_data:
                csv_input = trouble

            session['order'] = order
            session['filename'] = filename
            session['input_encoding'] = input_encoding
            session['output_encoding'] = ''
            return render_template('index.html', csv_input=csv_input, perso_mest=perso_mest,
                                   status='done', tiraz=tiraz)

        elif "calculation" in request.form:
            form = request.form
            session['places'] = places = int(form['places'])
            session['pile'] = pile = int(form['pile'])
            csv_input, _ = read_n_lines(input_file, n)

            input_encoding = session['input_encoding']

            tiraz, perso_mest, pile_size, izdeliy_v_privertke, full_pile_amount, hvost_izdeliy, \
            hvost_listov, dummy = privertka(input_file, pile, places, input_encoding)

            csv_output, session['output_encoding'] = read_n_lines(converted_file, n)

            return render_template('index.html', csv_input=csv_input, csv_output=csv_output,
                                   places=places, pile_size=pile_size, tiraz=tiraz,
                                   perso_mest=perso_mest, izdeliy_v_privertke=izdeliy_v_privertke,
                                   full_pile_amount=full_pile_amount, hvost_izdeliy=hvost_izdeliy,
                                   hvost_listov=hvost_listov, dummy=dummy, status='')

        elif "download" in request.form:
            download_file = "csvoutput.csv"
            return send_file(download_file, as_attachment=True)

        elif "perekladka" in request.form:
            download_file = "perekladka.csv"
            attachment_filename = download_file + "_" + str(session['places']) + "_" + str(session['pile'])+'.csv'
            input_file = "csvinput.csv"
            perekladka(input_file)
            return send_file(download_file, as_attachment=True, attachment_filename=attachment_filename, mimetype='text/csv')

        elif "markirovka" in request.form:
            form = request.form
            pachka = int(form[''])
            _ = perekladka(input_file, pachka)
    else:
        return render_template('index.html')


def consistency(f, encoding):
    """
    Проверяем консистентность данных. Анализируем заголовок, понимаем сколько полей.
    Потом анализируем все строки на такое же кол-во данных.
    Заодно передаем дальше число строк (тираж)
    :param f (string) имя файла с данными (csv, который загружен пользователем)
    :param encoding (string) кодировка файла
    :return: tiraz (int) сколько строк в файле (без заголовка)
    :return: bad_data (bool) если найдено несоответствие, то True
    :return: text (string) текст о неконсистентности данных
    """
    with open(f, 'r', encoding=encoding) as csv_string:
        content = csv.reader(csv_string, delimiter=',')
        header = next(content, None)
        columns = len(header)
        print('Кол-во полей в заголовке:', len(header))
        bad_data = False
        text = ''
        for i, row in enumerate(content):
            tiraz = i
            row_len = len(row)
            if row_len != columns:
                print(f'ERROR: line {i+1}, contain {row_len} item!')
                text += f'ERROR: line {i+1}, contain {row_len} item!\n'
                bad_data = True
        tiraz += 1
        return tiraz, columns, bad_data, text


if __name__ == '__main__':
    app.run()
