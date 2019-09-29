import requests
import json
import os
import sqlite3
from datetime import datetime, timedelta


class CommitConnection:
    @staticmethod
    def getCommitsInYear(year_lookup, username):
        response = requests.get("https://github-contributions-api.now.sh/v1/" + username)
        jsonResponse = json.loads(response.text)
        for year in jsonResponse["years"]:
            if year['year'] == str(year_lookup):
                return year['total']
        return 0

    @staticmethod
    def getTotalCommits(username):
        response = requests.get("https://github-contributions-api.now.sh/v1/" + username)
        jsonResponse = json.loads(response.text)
        count = 0
        for year in jsonResponse["years"]:
            count = count + year['total']
        return count



class DatabaseController:

    def __init__(self) -> None:
        super().__init__()
        if "GYC_DATABASE" in os.environ:
            self.database = os.environ['GYC_DATABASE']
        else:
            self.database = "database"

    def getPassword(self):
        database = sqlite3.connect(self.database)
        result = database.execute("SELECT value FROM settings WHERE setting='password'")
        result_fetched = result.fetchall()
        if len(result_fetched) == 1:
            database.close()
            return result_fetched[0][0]
        database.close()

    def get_setting(self, setting):
        database = sqlite3.connect(self.database)
        result = database.execute("SELECT value FROM settings WHERE setting=?", (setting,))
        result_fetched = result.fetchall()
        if len(result_fetched) == 1:
            database.close()
            return result_fetched[0][0]
        database.close()

    def set_setting(self, setting, value):
        database = sqlite3.connect(self.database)
        database.execute("UPDATE settings SET value=? WHERE setting=?", (value, setting))
        database.commit()
        database.close()

    def get_participants(self):
        database = sqlite3.connect(self.database)
        result = database.execute("SELECT username FROM participant")
        result_fetched = result.fetchall()
        database.close()
        return result_fetched

    def add_participants(self, user):
        database = sqlite3.connect(self.database)
        database.execute("INSERT INTO participant (username) VALUES (?)", (user,))
        database.commit()
        database.close()

    def remove_participants(self, user):
        database = sqlite3.connect(self.database)
        database.execute("DELETE FROM participant WHERE username=?", (user,))
        database.commit()
        database.close()

    def set_user_attribute(self, username, attribute, value):
        database = sqlite3.connect(self.database)
        database.execute("UPDATE user SET " + attribute + "=? WHERE username=?", (value, username))
        database.commit()
        database.close()

    def get_users_names(self):
        database = sqlite3.connect(self.database)
        users = database.execute("SELECT username FROM user")
        users = users.fetchall()
        if len(users) > 0:
            userList = []
            for user in users:
                userList.append(user[0])
            database.close()
            return userList
        else:
            database.close()
            return []

    def get_user_by_name(self, username):
        database = sqlite3.connect(self.database)
        users = database.execute("SELECT * FROM user WHERE username=?", (username,))
        user = users.fetchone()
        return user

    def return_user_with_name_and_password(self, user, passwordHash):
        database = sqlite3.connect(self.database)
        users = database.execute("SELECT * FROM user WHERE username=?", (user,))
        users = users.fetchall()
        if len(users) > 0:
            if users[0][1] == passwordHash:
                return users[0]
            else:
                return False
        else:
            return False
