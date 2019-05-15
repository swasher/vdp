import chardet
from io import StringIO


def read_n_lines(f, n):
    txt = ""
    try:
        with open(f, 'rb') as csv_bytes:
            rawdata = csv_bytes.read()
            charenc = chardet.detect(rawdata)['encoding'] # todo VERY HEAVY OPERATION
            csv_string = StringIO(rawdata.decode(charenc))
            txt = ''.join([r for r in csv_string][:10])
            # for i in range(n):
            #     txt += csv_string.readline()
    except FileNotFoundError:
        txt = 'FileNotFoundError'
    return txt
