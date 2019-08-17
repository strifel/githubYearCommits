import requests as http
import json
from datetime import datetime, timedelta
from src.Util import sortWithCount


class Participant:

    def __init__(self, username) -> None:
        super().__init__()
        self.username = username
        response = http.get("https://api.github.com/users/" + username + "/repos?per_page=100")
        self.repos = json.loads(response.text)
        response = http.get("https://github-contributions-api.now.sh/v1/" + username)
        self.contributions = json.loads(response.text)

    def get_languages(self):
        languages = {}
        for repository in self.repos:
            language = repository['language']
            if language is None:
                language = "None"
            if language in languages and "count" in languages[language]:
                languages[language]["count"] += 1
            else:
                languages.update({language: {"language": language, "count": 1}})
        return sortWithCount(languages)

    def get_commit_mail(self):
        if len(self.repos) > 0:
            commit_url = self.repos[0]['commits_url'].replace('{/sha}', '')
            json_commits = json.loads(http.get(commit_url).text)
            if json_commits[0]['author']['login'].lower() == self.username.lower():
                return json_commits[0]['commit']['author']['email']

    def get_commit_streak(self):
        streak = 0
        streakEnd = False
        while not streakEnd:
            date = datetime.now() - timedelta(days=streak + 1)
            for contribution in self.contributions["contributions"]:
                if contribution['date'] == datetime.now().strftime("%Y-%m-%d"):
                    if contribution['count'] > 0:
                        streak += 1
                elif contribution['date'] == date.strftime("%Y-%m-%d"):
                    if contribution['count'] > 0:
                        streak += 1
                    else:
                        streakEnd = True
                        break
        return streak

    def get_commits_in_year(self, year):
        for cYear in self.contributions["years"]:
            if cYear['year'] == str(year):
                return cYear['total']
        return 0
