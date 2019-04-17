from flask import Flask
from privertka import privertka

app = Flask(__name__)

app.config["DEBUG"] = True


@app.route('/')
def hello_world():
    return 'Привет, Мир!'


if __name__ == '__main__':
    app.run()
