import hashlib
import sqlite3
import os
import sys
from version import VERSION, DEV_STABLE, DEV
if DEV and "--continue-dev" not in sys.argv:
    continueInput = input("You are using a Dev version. This is not recommended. It is recommend to rollback to the "
                          "last stable commit with 'git checkout " + DEV_STABLE + "'. To continue type 'continue'")
    if continueInput != "continue":
        exit(0)
if len(sys.argv) > 1 and not sys.argv[1][0] == "-":
    pw = sys.argv[1]
else:
    pw = input("Your Admin password: ")
hashed = hashlib.sha256(pw.encode()).hexdigest() + ""
if "GYC_DATABASE" in os.environ:
    db = sqlite3.connect(os.environ['GYC_DATABASE'])
else:
    db = sqlite3.connect("database")
db.execute("CREATE TABLE IF NOT EXISTS settings (setting string PRIMARY KEY, value string)")
db.execute("INSERT INTO settings (setting, value) VALUES (?, ?)", ("cache", "1220"))
db.execute("INSERT INTO settings (setting, value) VALUES (?, ?)", ("allow-force", "true"))
db.execute("INSERT INTO settings (setting, value) VALUES (?, ?)", ("allow-user-unregistered", "true"))
db.execute("INSERT INTO settings (setting, value) VALUES (?, ?)", ("duration", "year"))
db.execute("INSERT INTO settings (setting, value) VALUES (?, ?)", ("dark-mode-default", "false"))
db.execute("INSERT INTO settings (setting, value) VALUES (?, ?)", ("show-commit-mail", "false"))
db.execute("INSERT INTO settings (setting, value) VALUES (?, ?)",
           ("jwtToken", input("Please enter some LONG random input. Its important. If it is too short your login will not be secure")))
db.execute("INSERT INTO settings (setting, value) VALUES (?, ?)", ("version", str(VERSION)))
db.execute("CREATE TABLE IF NOT EXISTS participant (username string PRIMARY KEY NOT NULL)")
db.execute("INSERT INTO participant (username) VALUES ('strifel')")
db.execute("CREATE TABLE IF NOT EXISTS user (username string PRIMARY KEY NOT NULL, password string NOT NULL, permission string, twofo string)")
db.execute("INSERT INTO user (username, password, permission) VALUES ('admin', ?, '*')", (hashed,))
db.execute("CREATE TABLE IF NOT EXISTS cache (context string PRIMARY KEY NOT NULL, content string, expire UNSIGNED BIGINT)")

db.commit()
db.close()
