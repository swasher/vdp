import chardet


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