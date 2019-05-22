import os
import chardet

ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS")


def read_n_lines(f, n):
    try:
        with open(f, 'rb') as csv_bytes:
            rawdata = csv_bytes.read()
            encoding = chardet.detect(rawdata[:n])['encoding']  # todo VERY HEAVY OPERATION
        with open(f, 'r', encoding=encoding) as csv_string:
            # csv_string = StringIO(rawdata.decode(encoding))
            # txt = ''.join([r for r in csv_string][:n])

            # txt = csv_string.readlines(n)(100)
            txt = [next(csv_string) for x in range(n)]
            txt = ''.join(txt)
    except FileNotFoundError:
        txt = 'FileNotFoundError'
        encoding = 'encoding FileNotFoundError'
    return txt, encoding


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def line_end_convert(file_path):
    # replacement strings
    WINDOWS_LINE_ENDING = b'\r\n'
    UNIX_LINE_ENDING = b'\n'

    with open(file_path, 'rb') as open_file:
        content = open_file.read()

    content = content.replace(UNIX_LINE_ENDING, WINDOWS_LINE_ENDING)

    with open(file_path, 'wb') as open_file:
        open_file.write(content)