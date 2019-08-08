import sqlite3
import os
from version import VERSION, DEV, DEV_STABLE
print("This is the update Script!")
print("This script will update your database after you updated the codebase")
print("Update the codebase with git pull, if you havent!")
print("Searching for database...")
# This file should be called by user after version update
# Every version update (normally) needs database changes
if "GYC_DATABASE" in os.environ:
    db = sqlite3.connect(os.environ['GYC_DATABASE'])
else:
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
    if DEV:
        print("You updated to a dev commit. Okay...")
        continueInput = input("Do you really want to continue (type continue to continue)? This is not a stable "
                              "version (Manually changing database values/resetting the database, could be needed)! "
                              "Recommended commit is " + DEV_STABLE + " ")
        if continueInput != "continue":
            print("Good choice!")
            exit(0)
        print("Ok. Updating.... (Your fault if you have to recreate the database. (rm database and python3 install.py)")
    else:
        exit(0)

# Check if version is prior 0.9
if version < 0.9:
    db.execute("INSERT INTO settings (setting, value) VALUES (?, ?)", ("duration", "year"))
    print("Updated to 0.9: You can now change the duration between year and eternity")
# Check if version is prior 1.1 (Huge reworks)
if version < 1.1:
    db.execute("ALTER TABLE user RENAME TO participant")
    db.execute("INSERT INTO settings (setting, value) VALUES (?, ?)", ("dark-mode-default", "false"))
    print("Updated to 1.1: Enjoy new changes!")


db.execute("UPDATE settings SET value = ? WHERE setting = 'version'", (str(VERSION), ))
db.commit()
db.close()
