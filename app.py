# -*- coding: utf-8 -*-

from flask import Flask
from flask import send_file
from flask import request
from flask import render_template
from werkzeug.utils import secure_filename

from privertka import privertka
from markirovka import perekadka
from util import read_n_lines

import chardet

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=["GET", "POST"])
def main():
    N = 100
    input_file = "csvinput.csv"
    converted_file = "csvoutput.csv"
    if request.method == "POST":
        # if "files" in request:
        if len(request.files) > 0:
            f = request.files['csvinput']
            f.save(input_file)

            ENCODING = chardet.detect(f.getvalue())['encoding']

            lines = f.getvalue().decode(ENCODING)
            lines = '\n'.join(lines.split('\n')[:N])
            filename = secure_filename(f.filename)
            return render_template('index.html', csv_input=lines, tech=ENCODING, filename=filename)

        elif "calculation" in request.form:
            form = request.form
            places = int(form['places'])
            pile = int(form['pile'])
            csv_input = read_n_lines(input_file, N)

            tiraz, perso_mest, pile_size, izdeliy_v_privertke, full_pile_amount, hvost_izdeliy, \
            hvost_listov, dummy = privertka(input_file, pile, places)

            tech = render_template('tech_text.html', tiraz=tiraz, places=places, pile_size=pile_size,
                                   perso_mest=perso_mest, izdeliy_v_privertke=izdeliy_v_privertke,
                                   full_pile_amount=full_pile_amount, hvost_izdeliy=hvost_izdeliy,
                                   hvost_listov=hvost_listov, dummy=dummy)

            csv_output = read_n_lines(converted_file, N)

            return render_template('index.html', csv_input=csv_input, csv_output=csv_output,
                                   tech=tech, places=places, pile_size=pile_size)

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
    return send_file(download_file, as_attachment=True)


if __name__ == '__main__':
    app.run()
