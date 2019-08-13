import hashlib
import sqlite3
import os
from version import VERSION
pw = input("Your Admin password: ")
hashed = hashlib.sha256(pw.encode()).hexdigest() + ""
if "GYC_DATABASE" in os.environ:
    db = sqlite3.connect(os.environ['GYC_DATABASE'])
else:
    db = sqlite3.connect("database")
db.execute("CREATE TABLE IF NOT EXISTS settings (setting string PRIMARY KEY, value string)")
db.execute("INSERT INTO settings (setting, value) VALUES (?, ?)", ("password", hashed))
db.execute("INSERT INTO settings (setting, value) VALUES (?, ?)", ("cache", "1220"))
db.execute("INSERT INTO settings (setting, value) VALUES (?, ?)", ("allow-force", "true"))
db.execute("INSERT INTO settings (setting, value) VALUES (?, ?)", ("allow-user-unregistered", "true"))
db.execute("INSERT INTO settings (setting, value) VALUES (?, ?)", ("duration", "year"))
db.execute("INSERT INTO settings (setting, value) VALUES (?, ?)", ("dark-mode-default", "false"))
db.execute("INSERT INTO settings (setting, value) VALUES (?, ?)", ("version", str(VERSION)))
db.execute("CREATE TABLE IF NOT EXISTS participant (username string PRIMARY KEY NOT NULL)")
db.execute("INSERT INTO participant (username) VALUES ('strifel')")
db.commit()
db.close()
