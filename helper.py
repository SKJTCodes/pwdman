import datetime as dt
import operator
import re
from datetime import timedelta
import pickle

import bcrypt
import keyring
import pandas as pd
from pandas.tseries.offsets import BDay


def creds_man(app_name, uname, mode="store", pw=None):
    """
    encrypt string with bcrypt and store encrypted string with keyring.
    check keyring data from windows cred manager
    :param app_name: where to get password from
    :param uname: username
    :param mode: select between "store" and "check"
    :param pw: password
    :return:
    """
    assert mode == "store" or mode == "check", "Selected mode is unavailable"
    assert pw is not None, "Please include password to encrypt or password to be checked."

    if mode == "store":
        hashed = bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode('utf-8')
        keyring.set_password(app_name, uname, hashed)
        return hashed
    else:
        dec_pw = keyring.get_password(app_name, uname).encode('utf-8')
        return bcrypt.checkpw(pw.encode(), dec_pw)


def pickle_file(mode, fname="./pickle_data.pickle", data=None):
    """
    read/write data to a pickle file
    :param mode: types: "read", "write". choose between read and write operation
    :param fname: file location of data
    :param data: data to write. only required if mode is "write".
    :return: if read, returns file data else return file location
    """
    assert mode == "read" or mode == "write", "mode does not exist."

    if mode == "read":
        with open(fname, 'rb') as r:
            return pickle.load(r)
    else:
        assert data is not None, f"mode: {mode}, please use the data parameter to add data to pickle."
        with open(fname, 'wb') as w:
            pickle.dump(data, w)
        return fname


def sort_num_string(data_list):
    """
    Sort Strings that have numerical values by the numeric values
    :param data_list: list of strings
    :return: sorted list
    """

    def atoi(text):
        return int(text) if text.isdigit() else text

    def natural_keys(text):
        """
        alist.sort(key=natural_keys) sorts in human order
        http://nedbatchelder.com/blog/200712/human_sorting.html
        (See Toothy's implementation in the comments)
        """
        return [atoi(c) for c in re.split(r'(\d+)', text)]

    data_list.sort(key=natural_keys)
    return data_list


def date_delta(date=None, delta=0, out_fmt="%Y%m%d", in_fmt=None, biz_day=False):
    """
    Get Date or Date difference
    :param date: datetime object or string, date you want to perform operator on, default get current date
    :param delta: int value, add or subtract
    :param out_fmt: string, date output format, e.g. "%Y%m%d", None if out is datetime
    :param in_fmt: string, format of date param, if is string
    :param biz_day: compute delta by using Business Days or not
    :return: output date in string format
    """

    if date is None:
        date = dt.datetime.today()
    elif type(date) is str:
        assert in_fmt is not None
        date = pd.to_datetime(date, in_fmt)

    op = {"add": operator.add, "sub": operator.sub}

    if delta == 0:
        n_date = date
    else:
        key = "add" if delta > 0 else "sub"
        n_date = op[key](date, BDay(abs(delta)) if biz_day else timedelta(days=abs(delta)))

    return n_date if out_fmt is None else n_date.strftime(out_fmt)
