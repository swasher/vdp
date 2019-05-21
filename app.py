from flask import Flask
from flask import send_file
from flask import request
from flask import render_template
from werkzeug.utils import secure_filename

from privertka import privertka
from markirovka import perekadka
from util import read_n_lines
from util import allowed_file

import chardet

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=["GET", "POST"])
def main():
    n = N
    input_file = "csvinput.csv"
    converted_file = "csvoutput.csv"
    if request.method == "POST":
        # if "files" in request:
        # if len(request.files) > 0:
        if 'csvinput' in request.files:
            f = request.files['csvinput']
            if f and allowed_file(f.filename):
                # filename = secure_filename(file.filename)
                f.save(input_file)

            csv_input, encoding = read_n_lines(input_file, n)
            filename = secure_filename(f.filename)
            return render_template('index.html', csv_input=csv_input, tech=encoding, filename=filename)

        elif "calculation" in request.form:
            form = request.form
            places = int(form['places'])
            pile = int(form['pile'])
            csv_input, _ = read_n_lines(input_file, n)

            tiraz, perso_mest, pile_size, izdeliy_v_privertke, full_pile_amount, hvost_izdeliy, \
            hvost_listov, dummy = privertka(input_file, pile, places)

            csv_output, encoding = read_n_lines(converted_file, n)

            tech = render_template('tech_text.html', tiraz=tiraz, places=places, pile_size=pile_size,
                                   perso_mest=perso_mest, izdeliy_v_privertke=izdeliy_v_privertke,
                                   full_pile_amount=full_pile_amount, hvost_izdeliy=hvost_izdeliy,
                                   hvost_listov=hvost_listov, dummy=dummy, enc=encoding)

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
