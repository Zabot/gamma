import argparse
import gamma.store
import secrets
import sys
import pyperclip

from getpass import getpass
from pathlib import Path

passwordCharSet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,./;'[]\\-=`<>?:\"{}|~!@#$%^&*()_+"
def gen_password():
    return secrets.token_hex(32)

def create_account(default_name):
    name = input("Account Name [{}]: ".format(default_name))
    if not name:
        name = default_name

    user = input("Username []: ")

    password = None
    while not password:
        password = getpass("Password [Random]: ")
        if not password:
            password = gen_password()
        else:
            c_password = getpass("Confirm password: ")
            if c_password != password:
                print("Password mismatch")
                print()
                password = None

    save = input("Commit (y/[n]):") in ["y", "Y"]

    return gamma.store.Account(name, user, password) if save else None

def dump_account(account):
    print()
    print(account.name)
    print("-" * len(account.name))
    print("Username: {}".format(account.user))

    pyperclip.copy(account.password)
    print("Password copied to clipboard")

def main(args=None):

    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description='Password managment utility')
    parser.add_argument('name', 
            nargs="?", 
            default='', 
            metavar='account_name', 
            help='The account of interest. Omitting this parameter will list'
                 ' all account names. Entering a name that cannot be confidently'
                 ' resolved to a single account will list all of the matching accounts')

    parser.add_argument('-f', '--file', 
            default=str(Path.home()/'.passwords.db'),
            metavar='password_file',
            dest='file',
            help='Read accounts from file')

    parser.add_argument('-c', '--create', 
            action='store_true',
            dest='create',
            help='Create a new account')

    args = parser.parse_args()

    store = gamma.store.AccountStore(args.file, getpass())

    active_account = None

    if args.create:
        a = create_account(args.name);
        if a:
            store.store(a)
            dump_account(a)
            return 0
        else:
            print("Aborting...")

    search = store.search(args.name)
    if not search:
        print("No accounts found")
        return 0

    if len(search) == 1:
        dump_account(search[0])
        return 0

    print()
    if args.name:
        print("Found multiple potential matches:")

    for i, account in enumerate(search):
        print("[{}] {}".format(i, account.name))

    n = int(input("Select account: "))
    dump_account(search[n])
    return 0

if __name__ == "__main__":
    main()
