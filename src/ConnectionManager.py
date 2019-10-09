import requests
import json
import os
import sqlite3
import time


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
        result_fetched = self.execute_sql("SELECT value FROM settings WHERE setting='password'", [], False)
        if len(result_fetched) == 1:
            return result_fetched[0][0]

    def get_setting(self, setting):
        result_fetched = self.execute_sql("SELECT value FROM settings WHERE setting=?", (setting,), False)
        if len(result_fetched) == 1:
            return result_fetched[0][0]

    def set_setting(self, setting, value):
        self.execute_sql("UPDATE settings SET value=? WHERE setting=?", (value, setting), True)

    def get_participants(self):
        return self.execute_sql("SELECT username FROM participant", [], False)

    def add_participants(self, user):
        self.execute_sql("INSERT INTO participant (username) VALUES (?)", (user,), True)

    def remove_participants(self, user):
        self.execute_sql("DELETE FROM participant WHERE username=?", (user,), True)

    def set_user_attribute(self, username, attribute, value):
        self.execute_sql("UPDATE user SET " + attribute + "=? WHERE username=?", (value, username), True)

    def get_users_names(self):
        users = self.execute_sql("SELECT username FROM user", [], False)
        if len(users) > 0:
            userList = []
            for user in users:
                userList.append(user[0])
            return userList
        else:
            return []

    def get_user_by_name(self, username):
        database = sqlite3.connect(self.database)
        users = database.execute("SELECT * FROM user WHERE username=?", (username,))
        user = users.fetchone()
        return user

    def return_user_with_name_and_password(self, user, passwordHash):
        users = self.execute_sql("SELECT * FROM user WHERE username=?", (user,), False)
        if len(users) > 0:
            if users[0][1] == passwordHash:
                return users[0]
            else:
                return False
        else:
            return False

    def create_user(self, username, passwordHash, permissions):
        self.execute_sql("INSERT INTO user (username, password, permission) VALUES (?, ?, ?)", (username, passwordHash, permissions), True)

    def delete_user(self, username):
        self.execute_sql("DELETE FROM user WHERE username=?", (username,), True)

    def set_cache(self, context, content, tte):
        database = sqlite3.connect(self.database)
        database.execute("DELETE FROM cache WHERE context=?", (context,))
        database.execute("INSERT INTO cache (context, content, expire) VALUES (?, ?, ?)", (context, content, int(time.time() + tte)))
        database.commit()
        database.close()

    def get_cache(self, context):
        result = self.execute_sql("SELECT content, expire FROM cache WHERE context=?", (context,), False)
        if len(result) > 0:
            if result[0][1] < time.time():
                return False
            return result[0][0]
        else:
            return False

    def delete_cache(self, context):
        self.execute_sql("DELETE FROM cache WHERE context=?", (context,), True)

    def execute_sql(self, sql, params, commit):
        database = sqlite3.connect(self.database)
        result = database.execute(sql, params)
        if commit:
            database.commit()
            database.close()
        else:
            result = result.fetchall()
            database.close()
            return result
