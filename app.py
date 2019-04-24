from flask import Flask
from flask import send_file
from flask import request
from flask import render_template
from privertka import privertka

app = Flask(__name__)

app.config["DEBUG"] = True


@app.route('/', methods=["GET", "POST"])
def main():
    N = 3000
    if request.method == "POST":

        if "uploading" in request.form:
            f = request.files['csvinput']
            # file = open("csvinput.csv", "w")
            # file.write(f.content)
            # csv_input_text = f.read().decode("utf-8")
            f.save("csvinput.csv")

            # with open("csvinput.csv", 'r') as f:
            #     csv_input_text = f.readlines(5)

            csv_input_text = ""
            with open("csvinput.csv") as f:
                for i in range(N):
                    csv_input_text += f.readline()

            return render_template('index.html', csv_input_text=csv_input_text)
        elif "calculation" in request.form:
            form = request.form
            places = int(form['places'])
            pile = int(form['pile'])
            try:
                with open("csvinput.csv", 'r') as file:
                    csv_input_text = ""
                    with open("csvinput.csv") as f:
                        for i in range(N):
                            csv_input_text += f.readline()

                    tiraz, perso_mest, pile_size, izdeliy_v_privertke, full_pile_amount, hvost_izdeliy, hvost_listov, dummy = privertka(
                        "csvinput.csv", pile, places)

                    tech_text = """
Тираж: {}
На листе изделий: {}
В привертке листов: {}
Полей персонализации: {}
Изделий в целой привертке: {}
Кол-во целых приверток: {}
Хвост изделий: {}
Хвост листов: {}
Пустышек: {}""".format(tiraz, places, pile_size, perso_mest, izdeliy_v_privertke, full_pile_amount, hvost_izdeliy, hvost_listov, dummy)

            except FileNotFoundError:
                csv_input_text = 'empty'


            try:
                with open("csvoutput.csv", 'r') as file:
                    csv_ouput_text = ""
                    with open("csvoutput.csv") as f:
                        for i in range(N):
                            csv_ouput_text += f.readline()
            except FileNotFoundError:
                csv_ouput_text = 'empty'

            return render_template('index.html', csv_input_text=csv_input_text, csv_ouput_text=csv_ouput_text,
                                   tech_text=tech_text, places=places, pile_size=pile_size)

    else:
        return render_template('index.html')


@app.route('/download', methods=['GET', 'POST'])
def download():
    # For windows you need to use drive name [ex: F:/Example.pdf]
    path = "csvoutput.csv"
    return send_file(path, as_attachment=True)


if __name__ == '__main__':
    app.run()
