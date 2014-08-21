import random
import string
import os
from datetime import datetime
import time
from time import mktime
from hashlib import md5
# import exception

_SALT = 'Do1phin'

now = datetime.now


def unix_time(value=None):
    if not value:
        value = datetime.utcnow()
    try:
        return int(mktime(value.timetuple()))
    except AttributeError:
        return None


def flatten_dict(dct):
    if not dct:
        return None
    return dict([(str(k), dct.get(k)) for k in dct.keys()])


def md5digest(string=None):
    salted_str = string + _SALT
    return md5(salted_str.encode('utf-8')).hexdigest().upper()


def random_string(length):
    return ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(length))


def find_dict_in_list(l, cond):
    for i in l:
        if not l:
            continue
        for k, v in cond.iteritems():
            if i.get(k) != v:
                break
        else:
            return i


def now_timestamp():
    return int(time.time())


def ensure_dir(dir_path, raise_exception=True):
    if os.path.exists(dir_path):
        if os.path.isdir(dir_path):
            return True
        else:
            if raise_exception:
                raise IOError("the path has existed but is not a dir")
            else:
                return False
    else:
        os.mkdir(dir_path)


def download_file(filestream, filepath):
    with open(filepath, 'w+') as f:
        for chunk in filestream.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
        f.close()
