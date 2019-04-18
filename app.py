from flask import Flask
from flask import send_file
from flask import request
from flask import render_template
from privertka import privertka

app = Flask(__name__)

app.config["DEBUG"] = True


@app.route('/', methods=["GET", "POST"])
def hello_world():
    if request.method == "POST":
        method = {'method': "POST"}

        if "csvinputfile" in request.files:
            f = request.files['csvinputfile']
            # file = open("csvinput.csv", "w")
            # file.write(f.content)
            # csv_input_text = f.read().decode("utf-8")
            f.save("csvinput.csv")

            with open("csvinput.csv", 'r') as f:
                csv_input_text = f.read()

            return render_template('index.html', method=method, csv_input_text=csv_input_text)
        elif "pile" in request.form:
            form = request.form
            places = int(form['places'])
            pile = int(form['pile'])
            try:
                with open("csvinput.csv", 'r') as file:
                    csv_input_text = file.read()

                    tiraz, places, columns, pile_size, izdeliy_v_privertke, full_pile_amount, hvost_izdeliy, hvost_listov, dummy = privertka(
                        "csvinput.csv", pile, places)

            except FileNotFoundError:
                csv_input_text = 'empty'


            try:
                with open("csvoutput.csv", 'r') as file:
                    csv_ouput_text = file.read()
            except FileNotFoundError:
                csv_ouput_text = 'empty'

            return render_template('index.html', method=method, csv_input_text=csv_input_text, csv_ouput_text=csv_ouput_text)

    else:
        method = {'method': "NOT DEFINE"}
        return render_template('index.html', method=method)


@app.route('/download', methods=['GET', 'POST'])
def download():
    # For windows you need to use drive name [ex: F:/Example.pdf]
    path = "csvoutput.csv"
    return send_file(path, as_attachment=True)


if __name__ == '__main__':
    app.run()
