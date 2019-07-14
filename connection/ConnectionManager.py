import requests
import json
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

    @staticmethod
    def getCommitStreak(username):
        response = requests.get("https://github-contributions-api.now.sh/v1/" + username)
        jsonResponse = json.loads(response.text)
        streak = 0
        streakEnd = False
        while not streakEnd:
            date = datetime.now() - timedelta(days=streak)
            for contribution in jsonResponse["contributions"]:
                if contribution['date'] == date.strftime("%Y-%m-%d"):
                    if contribution['count'] > 0:
                        streak += 1
                    else:
                        streakEnd = True
                    break
        return streak



class DatabaseController:
    users = []

    @staticmethod
    def getPassword():
        database = sqlite3.connect("database")
        result = database.execute("SELECT value FROM settings WHERE setting='password'")
        result_fetched = result.fetchall()
        if len(result_fetched) == 1:
            database.close()
            return result_fetched[0][0]
        database.close()

    @staticmethod
    def get_setting(setting):
        database = sqlite3.connect("database")
        result = database.execute("SELECT value FROM settings WHERE setting='" + setting + "'")
        result_fetched = result.fetchall()
        if len(result_fetched) == 1:
            database.close()
            return result_fetched[0][0]
        database.close()

    @staticmethod
    def set_setting(setting, value):
        database = sqlite3.connect("database")
        database.execute("UPDATE settings SET value=? WHERE setting=?", (value, setting))
        database.commit()
        database.close()

    @staticmethod
    def get_user():
        if not DatabaseController.users:
            database = sqlite3.connect("database")
            result = database.execute("SELECT username FROM user")
            result_fetched = result.fetchall()
            if len(result_fetched) > 0:
                database.close()
                DatabaseController.users = result_fetched
                return result_fetched
            database.close()
        else:
            return DatabaseController.users

    @staticmethod
    def add_user(user):
        database = sqlite3.connect("database")
        database.execute("INSERT INTO user (username) VALUES (?)", (user,))
        database.commit()
        database.close()
        DatabaseController.users = []

    @staticmethod
    def remove_user(user):
        database = sqlite3.connect("database")
        database.execute("DELETE FROM user WHERE username=?", (user,))
        database.commit()
        database.close()
        DatabaseController.users = []
