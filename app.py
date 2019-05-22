import os
import re
from flask import Flask
from flask import session
from flask import send_file
from flask import request
from flask import render_template
from werkzeug.utils import secure_filename

from privertka import privertka
from markirovka import perekadka
from util import read_n_lines
from util import allowed_file
from util import line_end_convert

import chardet

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

            session['order'] = order
            session['filename'] = filename
            session['input_encoding'] = input_encoding
            return render_template('index.html', csv_input=csv_input)

        elif "calculation" in request.form:
            form = request.form
            session['places'] = places = int(form['places'])
            session['pile'] = pile = int(form['pile'])
            csv_input, _ = read_n_lines(input_file, n)

            tiraz, perso_mest, pile_size, izdeliy_v_privertke, full_pile_amount, hvost_izdeliy, \
            hvost_listov, dummy = privertka(input_file, pile, places)

            csv_output, session['output_encoding'] = read_n_lines(converted_file, n)

            return render_template('index.html', csv_input=csv_input, csv_output=csv_output,
                                   places=places, pile_size=pile_size, tiraz=tiraz,
                                   perso_mest=perso_mest, izdeliy_v_privertke=izdeliy_v_privertke,
                                   full_pile_amount=full_pile_amount, hvost_izdeliy=hvost_izdeliy,
                                   hvost_listov=hvost_listov, dummy=dummy)

        elif "download" in request.form:
            download_file = "csvoutput.csv"
            return send_file(download_file, as_attachment=True)

        elif "perekladka" in request.form:
            form = request.form
            pachka = int(form[''])
            _ = perekladka(input_file, pachka)

        elif "markirovka" in request.form:
            form = request.form
            pachka = int(form[''])
            _ = perekladka(input_file, pachka)
    else:
        return render_template('index.html')


# @app.route('/download', methods=['GET', 'POST'])
# def download():
#     download_file = "csvoutput.csv"
#     return send_file(download_file, as_attachment=True)


@app.route('/perekladka', methods=['GET', 'POST'])
def perekladka():
    download_file = "csvoutput.csv"
    # line_end_convert(download_file)
    attachment_filename = download_file+"_"+session['places']+"_"+session['pile']
    attachment_filename = '3333'
    return send_file(download_file, attachment_filename=attachment_filename, mimetype='text/csv')


if __name__ == '__main__':
    app.run()
