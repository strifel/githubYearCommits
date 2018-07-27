import requests
import json


class CommitConnection:
    @staticmethod
    def getCommitsInYear(year, username):
        response = requests.get("https://github-contributions-api.now.sh/v1/" + username)
        jsonResponse = json.loads(response.text)
        count = 0
        for contribution in jsonResponse["contributions"]:
            if contribution["date"].startswith(year + "-"):
                count = count + contribution["count"]
        return count
