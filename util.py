import os
import chardet
import sys
from flask import current_app
from chardet.universaldetector import UniversalDetector


ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS")


# DEPRECATED
# @app.route('/create_empty', methods=['POST'])
# def create_empty(name, size):
#     path = os.path.join(app.config['DATA_DIR'], name)
#     with open(path, "wb") as f:
#         f.seek(int(size) - 1)
#         f.write(b"\0")


def read_n_lines(f, n, encoding):
    """
    :param f: имя файла
    :param n: кол-во строк
    :return: string, первые n строк из файла f
    """
    from datetime import datetime
    try:

        # DEPRECATED DUE LONG OPERATION (ABOUT 9-13 SEC ON HEAVY FILE)
        # detector = UniversalDetector()
        # with open(f, 'rb') as csv_bytes:
        #     k = datetime.now()
        #     for row in csv_bytes:
        #         detector.feed(row)
        #         if detector.done: break
        #
        # print(datetime.now() - k)
        # detector.close()
        # encoding = detector.result['encoding']

        # DEPRECATED; Now encoding is input parameter
        # k = datetime.now()
        # with open(f, 'rb') as csv_bytes:
        #     rawdata = csv_bytes.read()
        #     encoding = chardet.detect(rawdata)['encoding']  # heavy operation if dont provide :n
        # print(datetime.now() - k)

        # todo вынести определение кодировки из этой функции, это нужно делать только один раз

        # working code
        # with open(f, 'r', encoding=encoding) as csv_string:
        #     # txt = csv_string.readlines(n)(100)
        #     strings = [next(csv_string).rstrip() for x in range(n+1)]
        #     txt = '\n'.join(strings)

        txt = ''
        with open(f, 'r', encoding=encoding) as csv_string:
            for i in range(n):
                txt += csv_string.readline()

    except FileNotFoundError:
        txt = 'FileNotFoundError'
        encoding = 'FileNotFoundError'
    return txt


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def line_end_convert(file_path):
    # replacement strings
    WINDOWS_LINE_ENDING = b'\r\n'
    UNIX_LINE_ENDING = b'\n'

    with open(file_path, 'rb') as open_file:
        content = open_file.read()

    content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)

    with open(file_path, 'wb') as open_file:
        open_file.write(content)



def try_utf8(file_name):
    """
    Возвращает строку. Если файл в кодировке utf-8, возвращает 'utf-8', иначе деволтное значение.
    :param file_name:
    :return: string
    """

    with open(file_name, 'rb') as f:
        data = f.read()

    try:
        data.decode('utf-8')
        return 'utf-8'
    except UnicodeDecodeError:
        return current_app.config['NON_UTF_INPUT_ENC']