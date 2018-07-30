import bcrypt
import hashlib
import secrets
import sqlite3

from Crypto.Cipher import AES
from fuzzywuzzy import process

class UninitalizedStore(Exception):
    pass

def _pad(s, boundry):
    padding = boundry - (len(s) % boundry)
    return s + chr(padding) * padding

def _unpad(s, boundr):
    return s[:-(s[-1])]

class Account:
    def __init__(self, name, user, password):
        self.name = name
        self.user = user
        self.password = password

    def __str__(self):
        return self.name

class AccountStore:
    def __init__(self, path, key):
        self.conn = sqlite3.connect(path)
        key = key.encode("ascii")

        try:
            if not self.test_key(key):
                print("Failed to decrypt password store")
                exit(1)
        except UninitalizedStore:
            self.initalize(key)

        self.key = hashlib.sha256(key).digest()

    def __del__(self):
        self.conn.commit()
        self.conn.close()

    def test_key(self, key):
        c = self.conn.cursor()

        try:
            c.execute("SELECT data FROM metadata")
        except sqlite3.OperationalError:
            raise UninitalizedStore()

        row = c.fetchone()

        if not row:
            raise UninitalizedStore()

        return bcrypt.checkpw(key, row[0])

    def initalize(self, key):
        c = self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS metadata (data TEXT)")
        c.execute("INSERT INTO metadata VALUES (?)", 
                  (bcrypt.hashpw(key, bcrypt.gensalt()),))
        c.execute("CREATE TABLE IF NOT EXISTS accounts("
                     "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "account_name TEXT NOT NULL,"
                     "user_name TEXT NOT NULL,"
                     "password TEXT NOT NULL)")

    def store(self, account):
        c = self.conn.cursor()
        iv = secrets.token_bytes(AES.block_size)

        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        name = cipher.encrypt(_pad(account.name, AES.block_size))
        user = cipher.encrypt(_pad(account.user, AES.block_size))
        password = cipher.encrypt(_pad(account.password, AES.block_size))

        c.execute("INSERT INTO accounts (account_name, user_name, password)"
                  "VALUES (?, ?, ?)", (iv+name, user, password))

    def load(self, id):
        c = self.conn.cursor()
        c.execute("SELECT account_name, user_name, password "
                  "FROM accounts WHERE id = ?", (id,));

        row = c.fetchone()

        decipher = AES.new(self.key, AES.MODE_CBC, row[0][:16])

        name = _unpad(decipher.decrypt(row[0][16:]), AES.block_size).decode("ascii")
        user = _unpad(decipher.decrypt(row[1]), AES.block_size).decode("ascii")
        password = _unpad(decipher.decrypt(row[2]), AES.block_size).decode("ascii")
        return Account(name, user, password)

    def search(self, search_term):
        c = self.conn.cursor()
        c.execute("SELECT id FROM accounts");
        accounts = [self.load(r[0]) for r in c.fetchall()]

        if search_term:
            matched = process.extract(search_term, accounts)

            if not matched:
                return []

            ret = [matched[0]]

            for m in matched[1:]:
                if ret[-1][1] - m[1] < 5:
                    ret.append(m)

            return list(map(lambda x: x[0], ret))

        return accounts

