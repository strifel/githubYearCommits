from sqlite3 import IntegrityError

from flask import render_template, make_response, send_from_directory, send_file, request, Flask
import requests as rest
import json
from hashlib import sha256
from src.ConnectionManager import CommitConnection
from src.ConnectionManager import DatabaseController
from src.Participant import Participant
from datetime import datetime
import operator

app = Flask(__name__, static_url_path='')
# not needed but I am afraid deleting it.
users = list()
timeUpdated = 0
database = DatabaseController()


@app.route('/', methods=['GET'], defaults={"reload": False})
@app.route('/force', methods=['GET'], defaults={"reload": True})
def main_page(reload):
    global timeUpdated
    global users
    timespan = ""
    duration = database.get_setting("duration")
    year = ""
    if duration == "year":
        year = datetime.now().strftime("%Y")
    if (reload and (database.get_setting("allow-force") == "true" or
                    request.cookies.get("gyc_login") == database.getPassword())) or \
            datetime.now().timestamp() - timeUpdated > database.get_setting("cache"):
        users = list()
        timeUpdated = datetime.now().timestamp()
        user_contributions = {}
        for user in database.get_participants():
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


@app.route('/participant/<string:participant>', methods=['GET'])
def participant_page(participant):
    return make_response(send_file("web/participant.html"))


@app.route('/login', methods=['GET'])
@app.route('/admin', methods=['GET'])
def admin():
    if request.cookies.get("gyc_login") == database.getPassword():
        resp = make_response(send_file("web/admin.html"))
        return resp
    else:
        resp = make_response(send_file("web/login.html"))
        resp.delete_cookie("gyc_login")
        return resp


@app.route('/api/participants/<string:username>', methods=['POST', 'DELETE'])
@app.route('/api/participants', methods=['GET'], defaults={"username": None})
def participants(username):
    if request.cookies.get("gyc_login") == database.getPassword():
        if request.method == 'GET':
            entries = []
            for row in database.get_participants():
                entries.append(row[0])
            resp = make_response(json.dumps(entries))
            resp.headers['Content-Type'] = 'application/json'
            return resp
        elif request.method == 'POST':
            try:
                database.add_participants(username)
            except IntegrityError:
                resp = make_response(json.dumps({"error": "Participant already exists"}), 400)
            else:
                resp = make_response(json.dumps({"message": "Added participant!"}), 201)
            resp.headers['Content-Type'] = 'application/json'
            return resp
        elif request.method == 'DELETE':
            database.remove_participants(username)
            resp = make_response(json.dumps({"message": "Removed participant!"}))
            resp.headers['Content-Type'] = 'application/json'
            return resp
            pass


@app.route('/api/participants/<string:username>', methods=['GET'])
def participant_api(username):
    # Checking if participant exists in database if unregistered not allowed
    if database.get_setting("allow-user-unregistered") == "false":
        found = False
        for dbUser in database.get_participants():
            if dbUser[0] == username:
                found = True
        if not found:
            return make_response(json.dumps({"error": "User not found"}), 404, {"Content-Type": "application/json"})
    # Finding year in query string
    if "contributions_year" in request.args:
        year = int(request.args['contributions_year'])
    else:
        year = int(datetime.now().strftime("%Y"))
    # Create Participant Object and response
    participant = Participant(username)
    resp = make_response(
        json.dumps(
            {
                "general": {
                    "username": participant.username,
                    "commit_mail": None if database.get_setting("show-commit-mail") == "false" else participant.get_commit_mail(),
                },
                "languages": participant.get_languages(),
                "stats": {
                    "contributions": {
                        "year": year,
                        "contributions": participant.get_commits_in_year(year)
                    },
                    "contribution_streak": participant.get_commit_streak()
                }
            }
        ),
        {"Content-Type": "application/json"}
    )
    resp.headers['Cache-Control'] = "no-cache, no-store, must-revalidate"
    resp.headers['Pragma'] = "no-cache"
    resp.headers['Expires'] = "0"
    return resp


@app.route('/api/setting/<string:settingName>', methods=['GET', 'PUT'])
def setting(settingName):
    # Allow access only with login, or to dark mode variable
    if request.cookies.get("gyc_login") == database.getPassword() \
            or (settingName == "dark-mode-default" and request.method == 'GET'):
        if request.method == 'PUT':
            if 'value' in request.json:
                value = request.json['value']
                if settingName == "password":
                    value = sha256(value.encode()).hexdigest()
                database.set_setting(settingName, value)
        resp = make_response(json.dumps({"name": settingName, "value": database.get_setting(settingName)}))
        resp.headers['Content-Type'] = 'application/json'
        return resp
    else:
        resp = make_response(json.dumps({"error": "Login not found"}))
        resp.headers['Content-Type'] = 'application/json'
        resp.status_code = 403
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
    print("Closing down...")
