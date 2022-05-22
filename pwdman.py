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
    log.info("Validation Successful ...")

    # run add feature or view feature
    c = h.Crypto()
    c.set_key(h.creds_man("pwdman", usr, mode="get_keyring"), replace=True)

    cred_df = read_creds(args.cred_file)

    if args.mode == "add":
        cred_df = add(c, cred_df)

        log.info(f"Saving Creds to {args.cred_file}")
        cred_df.to_csv(args.cred_file, index=False)

    elif args.mode == "mass_upload":
        assert args.mass_file.is_file(), f"File not found. {args.mass_file}"

        df = pd.read_csv(args.mass_file)
        for i, r in df.iterrows():
            cred_df = add(c, cred_df, r)

        log.info(f"Saving Creds to {args.cred_file}")
        cred_df.to_csv(args.cred_file, index=False)

    else:
        while True:
            srch = input("Search: ")
            if srch.lower() == "q":
                log.info("Quit")
                return

            elif srch == "*":
                srch = ".*"

            df = view(c, cred_df, srch)

            if df.shape[0] == 0:
                log.warning("No Results Found.")

            else:
                print(df)


def view(c, cred_df, search):
    """
    view all creds
    :param c: crypto class, used for decrypt or encrypt text
    :param cred_df: credential vault DataFrame
    :param search: regex search result
    :return: vault dataframe
    """
    log.info("Search Credentials ...")

    cred_df = cred_df.loc[(cred_df["Details"].str.contains("(?i)" + search, regex=True, na=False) |
                           cred_df["Category"].str.contains("(?i)" + search, regex=True, na=False))].copy()
    cred_df["Password"] = cred_df["Password"].apply(lambda x: c.decrypt(x))
    return cred_df


def read_creds(cred_path):
    """
    find and read creds file, if don't exist, will create an empty df
    :param cred_path: path to creds.csv
    :return: dataframe of creds
    """
    # create empty dataframe if file does not exist.
    if not cred_path.is_file():
        df = pd.DataFrame(columns=["Username", "Password", "Category", "Details"])
    else:
        if h.get_ext(cred_path) == ".csv":
            df = pd.read_csv(cred_path)
        else:
            assert False, f"file type: {h.get_ext(cred_path)}, not implemented for extraction"

    return df


def add(c, cred_df, creds=None):
    """
    add new creds to file
    :param c: crypto class, used for decrypt or encrypt text
    :param cred_df: credentials DataFrame
    :param creds: Credential to add, if None user will be prompted to key in
    :return: vault dataframe
    """
    if creds is None:
        log.info("Please Add Credential details ...")
        cat = input("Category: ")
        usr = input("Username: ")
        pwd = getpass.getpass("Password: ")
        det = input("Details: ")
    else:
        cat = creds["Category"]
        usr = creds["Username"]
        pwd = creds["Password"]
        det = creds["Details"]
        log.info(f"Added Credential details ({usr})...")

    data = {"Username": usr, "Password": c.encrypt(pwd), "Details": det, "Category": cat}

    cred_df = cred_df.append(data, sort=False, ignore_index=True)
    return cred_df


if __name__ == '__main__':
    main()
