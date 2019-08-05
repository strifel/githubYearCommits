from sqlite3 import IntegrityError

from flask import render_template, make_response, send_from_directory, send_file, request, Flask
import requests as rest
import json
from hashlib import sha256
from connection.ConnectionManager import CommitConnection
from connection.ConnectionManager import DatabaseController
from datetime import datetime
import operator

app = Flask(__name__, static_url_path='')
# not needed but I am afraid deleting it.
users = list()
timeUpdated = 0


@app.route('/', methods=['GET'], defaults={"reload": False})
@app.route('/force', methods=['GET'], defaults={"reload": True})
def main_page(reload):
    global timeUpdated
    global users
    timespan = ""
    duration = DatabaseController.get_setting("duration")
    year = ""
    if duration == "year":
        year = datetime.now().strftime("%Y")
    if (reload and (DatabaseController.get_setting("allow-force") == "true" or
                    request.cookies.get("gyc_login") == DatabaseController.getPassword())) or \
            datetime.now().timestamp() - timeUpdated > DatabaseController.get_setting("cache"):
        users = list()
        timeUpdated = datetime.now().timestamp()
        user_contributions = {}
        for user in DatabaseController.get_participants():
            if duration == "year":
                user_contributions.update({user[0]: CommitConnection.getCommitsInYear(year, user[0])})
            elif duration == "eternity":
                user_contributions.update({user[0]: CommitConnection.getTotalCommits(user[0])})
            else:
                user_contributions.update({user[0]: 0})
        sorted_contributions = sorted(user_contributions.items(), key=operator.itemgetter(1), reverse=True)
        for user in sorted_contributions:
            users.append({"name": user[0], "contributions": user[1]})
    if duration == "year":
        timespan = "in " + year
    elif duration == "eternity":
        timespan = "ever"
    # users.append({"name": user[0], "contributions": CommitConnection.getCommitsInYear(year, user[0])})
    # users.append(
    # users.append({"name": "robmroi03", "contributions": CommitConnection.getCommitsInYear(year, "robmroi03")})
    #    {"name": "felixletsplayyt", "contributions": CommitConnection.getCommitsInYear(year, "felixletsplayyt")})
    resp = make_response(render_template("index.html.twig", users=users, time=datetime.fromtimestamp(timeUpdated)
                                         .strftime('%H:%M:%S'), timespan=timespan))
    resp.headers['Cache-Control'] = "no-cache, no-store, must-revalidate"
    resp.headers['Pragma'] = "no-cache"
    resp.headers['Expires'] = "0"
    return resp


@app.route('/login', methods=['GET'])
@app.route('/admin', methods=['GET'])
def admin():
    if request.cookies.get("gyc_login") == DatabaseController.getPassword():
        resp = make_response(send_file("web/admin.html"))
        return resp
    else:
        resp = make_response(render_template("login.html.twig"))
        resp.delete_cookie("gyc_login")
        return resp


@app.route('/backend/participants/<string:username>', methods=['POST', 'DELETE'])
@app.route('/backend/participants', methods=['GET'], defaults={"username": None})
def participants(username):
    if request.cookies.get("gyc_login") == DatabaseController.getPassword():
        if request.method == 'GET':
            entries = []
            for row in DatabaseController.get_participants():
                entries.append(row[0])
            resp = make_response(json.dumps(entries))
            resp.headers['Content-Type'] = 'application/json'
            return resp
        elif request.method == 'POST':
            try:
                DatabaseController.add_participants(username)
            except IntegrityError:
                resp = make_response(json.dumps({"error": "Participant already exists"}), 400)
            else:
                resp = make_response(json.dumps({"message": "Added participant!"}), 201)
            resp.headers['Content-Type'] = 'application/json'
            return resp
        elif request.method == 'DELETE':
            DatabaseController.remove_participants(username)
            resp = make_response(json.dumps({"message": "Removed participant!"}))
            resp.headers['Content-Type'] = 'application/json'
            return resp
            pass


@app.route('/backend/setting/<string:settingName>', methods=['GET', 'PUT'])
def setting(settingName):
    # Allow access only with login, or to dark mode variable
    if request.cookies.get("gyc_login") == DatabaseController.getPassword() \
            or (settingName == "dark-mode-default" and request.method == 'GET'):
        if request.method == 'PUT':
            if 'value' in request.json:
                value = request.json['value']
                if settingName == "password":
                    value = sha256(value.encode()).hexdigest()
                DatabaseController.set_setting(settingName, value)
        resp = make_response(json.dumps({"name": settingName, "value": DatabaseController.get_setting(settingName)}))
        resp.headers['Content-Type'] = 'application/json'
        return resp
    else:
        resp = make_response(json.dumps({"error": "Login not found"}))
        resp.headers['Content-Type'] = 'application/json'
        resp.status_code = 403
        return resp


@app.route('/user/<string:user>/<int:year>', methods=['GET'])
@app.route('/user/<string:user>', methods=['GET'], defaults={"year": int(datetime.now().strftime("%Y"))})
def user_page(user, year):
    if DatabaseController.get_setting("allow-user-unregistered") == "false":
        found = False
        for dbUser in DatabaseController.get_participants():
            if dbUser[0] == user:
                found = True
        if not found:
            return make_response("<h1>User not found</h1>", 404)
    repos = rest.get("https://api.github.com/users/" + user + "/repos?per_page=100")
    repos_json = json.loads(repos.text)
    # languages
    languages = {}
    for repository in repos_json:
        language = repository['language']
        if languages.get(language) is not None:
            languages.update({language: languages.get(language) + 1})
        else:
            languages.update({language: 1})
    sorted_languages = sorted(languages.items(), key=operator.itemgetter(1), reverse=True)
    # mail
    commit_url = repos_json[0]['commits_url'].replace('{/sha}', '')
    json_commits = json.loads(rest.get(commit_url).text)
    mail = ""
    if json_commits[0]['author']['login'].lower() == user.lower():
        mail = json_commits[0]['commit']['author']['email']
    # commit streak
    commit_streak = CommitConnection.getCommitStreak(user)
    # response
    resp = make_response(render_template("user.html.twig", username=user, contributions=CommitConnection
                                         .getCommitsInYear(year, user), year=year, languages=sorted_languages, email=mail, streak=commit_streak))

    return resp

# Serve static directory
@app.route('/static/<string:path>', methods=['GET'])
def static_files(path):
    return send_from_directory('static/', path)

# Allow acme to pass for e.g. lets Encrypt certificate creation
@app.route('/.well-known/acme-challenge/<string:path>', methods=['GET'])
def acme(path):
    return send_from_directory('.well-known/acme-challenge/', path)


if __name__ == '__main__':
    app.run()
