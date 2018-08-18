import hashlib
import sqlite3
pw = input("Your Backend password: ")
hashed = hashlib.sha256(pw.encode()).hexdigest() + ""
db = sqlite3.connect("database")
db.execute("CREATE TABLE IF NOT EXISTS settings (setting string PRIMARY KEY, value string)")
db.execute("INSERT INTO settings (setting, value) VALUES (?, ?)", ("password", hashed))
db.execute("CREATE TABLE IF NOT EXISTS user (username string PRIMARY KEY)")
db.commit()
db.close()
