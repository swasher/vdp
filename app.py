import os
import re
import csv
from flask import Flask
from flask import session
from flask import send_file
from flask import request
from flask import render_template
from werkzeug.utils import secure_filename
from fpdf import FPDF

from privertka import privertka
from markirovka import do_perekladka
from util import read_n_lines
from util import allowed_file

app = Flask(__name__)
app.config['N'] = int(os.getenv("N"))
app.secret_key = os.getenv("SECRET_KEY")


@app.route('/', methods=["GET", "POST"])
def main():
    n = app.config['N']
    # input_file = "csvinput.csv"
    # converted_file = "csvoutput.csv"
    if request.method == "POST":
        if 'csvinput' in request.files:
            f = request.files['csvinput']
            if f and allowed_file(f.filename):
                input_file = secure_filename(f.filename)
                f.save(input_file)
            else:
                raise Exception('Not valid filename!')

            preview_input, input_encoding = read_n_lines(input_file, n)

            pattern = r'\d\d-\d\d\d\d'
            result = re.match(pattern, input_file)
            order = result.group(0) if result else None

            tiraz, perso_mest, bad_data, trouble = consistency(input_file, input_encoding)
            if bad_data:
                preview_input = trouble

            session['order'] = order
            session['input_file'] = input_file
            session['input_encoding'] = input_encoding
            session['output_encoding'] = ''
            return render_template('index.html', preview_input=preview_input, perso_mest=perso_mest,
                                   status='done', tiraz=tiraz)

        elif "calculation" in request.form:
            form = request.form
            session['places'] = places = int(form['places'])
            session['pile'] = pile = int(form['pile'])
            input_file = session['input_file']
            input_encoding = session['input_encoding']

            output_file = os.path.splitext(input_file)[0]+'_'+str(places)+'x'+str(pile)+'.csv'
            session['output_file'] = output_file
            preview_input, _ = read_n_lines(input_file, n)

            tiraz, perso_mest, pile_size, izdeliy_v_privertke, full_pile_amount, hvost_izdeliy, \
            hvost_listov, dummy = privertka(input_file, output_file, pile, places, input_encoding)

            preview_output, session['output_encoding'] = read_n_lines(output_file, n)

            return render_template('index.html', preview_input=preview_input, preview_output=preview_output,
                                   places=places, pile_size=pile_size, tiraz=tiraz,
                                   perso_mest=perso_mest, izdeliy_v_privertke=izdeliy_v_privertke,
                                   full_pile_amount=full_pile_amount, hvost_izdeliy=hvost_izdeliy,
                                   hvost_listov=hvost_listov, dummy=dummy, status='')

        elif "download" in request.form:
            output_file = session['output_file']
            return send_file(output_file, as_attachment=True)

        # elif "markirovka" in request.form:
        #     form = request.form
        #     pachka = int(form[''])
        #     _ = perekladka(input_file, pachka)

    else:
        session.pop('username', None)

        session['state'] = 'init'
        return render_template('index.html')

@app.route('/perekladka', methods=["GET", "POST"])
def perekladka():
    # elif "perekladka" in request.form:
    input_file = session['input_file']
    places = session['places']
    pile = session['pile']
    perekladka_filename = 'perekladka_'+os.path.splitext(input_file)[0] + '_' + str(places) + 'x' + str(pile) + '.csv'
    session['perekladka_filename'] = perekladka_filename

    do_perekladka(input_file, perekladka_filename)
    return send_file(perekladka_filename, as_attachment=True, attachment_filename=perekladka_filename, mimetype='text/csv')



@app.route('/markirovka', methods=["GET", "POST"])
def markirovka():
    pdf_name = 'mark.pdf'
    perekladka_filename = session['perekladka_filename']

    # if pdf_name.ex
    # os.remove(pdf_name)

    pdf = FPDF('P', 'mm', [100, 60])
    if os.getenv("FLASK_ENV") == 'production':
        font_path = '/app/static/DejaVuSans.ttf'
        encoding = 'utf-8'
    else:
        font_path = 'C:\\Windows\\Fonts\\DejaVuSans.ttf'
        encoding = 'windows-1251'
    pdf.add_font('DejaVuSans', '', font_path, uni=True)
    pdf.set_font('DejaVuSans', '', 12)
    pdf.set_auto_page_break(False, 0)

    with open(perekladka_filename, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f)
        for row in reader:
            pdf.add_page()

            txt = '\n'.join([row['order'], row['privertka'], row['pachka'], row['amount'], row['pers']])

            # pdf.cell(0, 0, row['order'], ln=2)
            # pdf.cell(0, 0, row['privertka'], ln=2)
            # pdf.cell(0, 0, row['pachka'], ln=2)
            # pdf.cell(0, 0, row['amount'], ln=2)
            # pdf.cell(0, 0, row['pers'], ln=2)

            pdf.set_xy(20, 15)
            pdf.multi_cell(0, 5, txt, 0, 'L')
            pdf.rect(0.1, 0.1, 99.8, 59.9)


    pdf.output(pdf_name, 'F')

    return send_file(pdf_name, as_attachment=True, mimetype='application/pdf')


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
