import sqlite3
from version import VERSION
print("This is the update Script!")
print("This script will update your database after you updated the codebase")
print("Update the codebase with git pull, if you havent!")
print("Searching for database...")
# This file should be called by user after version update
# Every version update (normally) needs database changes
db = sqlite3.connect("database")
print("Searching for version....")
versionRequest = db.execute("SELECT value FROM settings WHERE setting = 'version'").fetchall()
# Check if version tag even exists.
if len(versionRequest) < 1:
    db.execute("INSERT INTO settings (setting, value) VALUES ('version', ?)", (str(VERSION - 0.1), ))
    print("No version existed. Maybe you were on a version prior 1.0")
    versionRequest = db.execute("SELECT value FROM settings WHERE setting = 'version'").fetchall()
version = float(versionRequest[0][0])
# Check if version is already newest Version
if version == VERSION:
    print("Already on newest version!")
    exit(0)

# Check if version is prior 0.9
if version < 0.9:
    db.execute("INSERT INTO settings (setting, value) VALUES (?, ?)", ("duration", "year"))
    print("Updated to 0.9: You can now change the duration between year and eternity")

db.execute("UPDATE settings SET value = ? WHERE setting = 'version'", (str(VERSION), ))
db.commit()
db.close()
