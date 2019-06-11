import os
import re
import csv
import logging
import shutil
from pathlib import Path
from flask import jsonify

from flask import Flask
from flask import session
from flask import send_file
from flask import request
from flask import render_template
from flask import make_response
from werkzeug.utils import secure_filename
from fpdf import FPDF

from privertka import privertka
from markirovka import do_perekladka
from util import read_n_lines
from util import allowed_file

app = Flask(__name__)
app.config['N'] = int(os.getenv("N"))
app.config['DATA_DIR'] = 'upload'
app.secret_key = os.getenv("SECRET_KEY")


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('vdp')


@app.route('/clear_data_dir', methods=['POST'])
def clear_data_dir():
    try:
        mypath = app.config['DATA_DIR']
        # shutil.rmtree(mypath, ignore_errors=True)
        # os.mkdir(app.config['DATA_DIR'])
        for root, dirs, files in os.walk(mypath):
            for file in files:
                os.remove(os.path.join(root, file))
        print('delete ok')
        return jsonify(status=200)
    except:
        return jsonify(status=501)


# DEPRECATED
# @app.route('/create_empty', methods=['POST'])
# def create_empty(name, size):
#     path = os.path.join(app.config['DATA_DIR'], name)
#     with open(path, "wb") as f:
#         f.seek(int(size) - 1)
#         f.write(b"\0")



@app.route('/process_chunk', methods=['POST'])
def process_chunk():
    # Route to deal with the uploaded chunks
    # log.info(request.form)
    # log.info(request.files)
    n = app.config['N']
    current_chunk = int(request.form['dzchunkindex'])

    file = request.files['file']
    save_path = os.path.join(app.config['DATA_DIR'], file.filename)

    # request data:
    # dzuuid: 0e1bbd5b-260f-4d9b-a67f-534310f7df8a
    # dzchunkindex: 35
    # dztotalfilesize: 409
    # dzchunksize: 10
    # dztotalchunkcount: 41
    # dzchunkbyteoffset: 350
    # file: (binary)


    # my_file = Path(save_path)
    # if not my_file.is_file():
    #     size = int(request.form['dztotalfilesize'])
    #     with open(save_path, "wb") as f:
    #         f.seek(size - 1)
    #         f.write(b"\0")
    #         f.seek(0)

    input_file = save_path

    try:
        with open(save_path, 'ab+') as f:
            # Goto the offset, aka after the chunks we already wrote
            f.seek(int(request.form['dzchunkbyteoffset']))
            f.write(file.stream.read())
    except OSError:
        # log.exception will include the traceback so we can see what's wrong
        log.exception('Could not write to file')
        return make_response(("Couldn't write the file to disk", 500))

    total_chunks = int(request.form['dztotalchunkcount'])

    if current_chunk + 1 == total_chunks:
        # This was the last chunk, the file should be complete and the size we expect
        if os.path.getsize(save_path) != int(request.form['dztotalfilesize']):
            log.error(f"File {file.filename} was completed, "
                      f"but has a size mismatch."
                      f"Was {os.path.getsize(save_path)} but we"
                      f" expected {request.form['dztotalfilesize']} ")
            return make_response(('Size mismatch', 500))
        else:
            log.info(f'File {file.filename} has been uploaded successfully')
    else:
        log.debug(f'Chunk {current_chunk + 1} of {total_chunks} '
                  f'for file {file.filename} complete')

    return make_response(("Chunk upload successful", 200))



@app.route('/', methods=["GET", "POST"])
def main():
    if not os.path.exists('upload'):
        os.mkdir('upload')
    n = app.config['N']
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
    input_file = session['input_file']
    places = session['places']
    pile = session['pile']
    perekladka_filename = 'perekladka_' + os.path.splitext(input_file)[0] + '_' + str(places) + 'x' + str(pile) + '.csv'
    do_perekladka(input_file, perekladka_filename)

    pdf_name = 'mark.pdf'

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
