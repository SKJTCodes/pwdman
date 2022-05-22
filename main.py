import pandas as pd

import helper as h
from Logger import Logger
from Parameter import Parameters
import getpass
from pathlib import Path

""" Initializing Script Parameters """
args = Parameters(description="Python Password Management").parse()

""" Initializing Logging Properties """
log_path = args.var_dir / "log" / f"debug-{h.date_delta(out_fmt='%Y%m%d-%H%M.%S')}.log"
log = Logger(log_path).get_logger()


def main():
    assert args.mode == "add" or args.mode == "view", f"Mode: {args.mode}, does not exist."

    # Get Username and Password
    if args.masteruser is None:
        usr = input("Master Username: ")
    else:
        usr = args.masteruser

    if args.masterpwd is None:
        pwd = getpass.getpass("Master Password: ")
    else:
        pwd = args.masterpwd

    # Check if password matches with keyring and set password as key for decryption
    log.info("Validating Credentials ...")
    assert h.creds_man("pwdman", usr, mode="check", pw=pwd), "Failed to Validate Credentials"

    # run add feature or view feature
    c = h.Crypto()
    c.set_key(h.creds_man("pwdman", usr, mode="get_keyring"), replace=True)

    if args.mode == "add":
        cred_df = read_creds(args.cred_file)
        cred_df = add(c, cred_df)
        log.info(f"Saving Creds to {args.cred_file}")
        cred_df.to_csv(args.cred_file, index=False)
    else:
        view(c)


def view(c):
    """
    view all creds
    :param c: crypto class, used for decrypt or encrypt text
    :return:
    """
    pass


def read_creds(cred_path):
    # create empty dataframe if file does not exist.
    if not cred_path.is_file():
        df = pd.DataFrame(columns=["Username", "Password", "Details"])
    else:
        if h.get_ext(cred_path) == ".csv":
            df = pd.read_csv(cred_path)
        else:
            assert False, f"file type: {h.get_ext(cred_path)}, not implemented for extraction"

    return df


def add(c, cred_df):
    """
    add new creds to file
    :param c: crypto class, used for decrypt or encrypt text
    :param cred_df: credentials DataFrame
    :return:
    """
    log.info("Please Add Credential details ...")

    det = input("Details: ")
    usr = input("Username: ")
    pwd = getpass.getpass("Password: ")

    data = {"Username": usr, "Password": c.encrypt(pwd), "Details": det}

    cred_df = cred_df.append(data, sort=False, ignore_index=True)
    return cred_df


if __name__ == '__main__':
    main()
