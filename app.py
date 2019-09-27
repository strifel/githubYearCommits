from sqlite3 import IntegrityError
from src.Helper import returnError
from flask import render_template, make_response, send_from_directory, send_file, request, Flask, g
from src.Settings import validSettings as validSettingValues
import re
import json
import jwt
import time
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


def verify_jwt(req, permissionsRequired):
    try:
        if 'Authorization' not in req.headers:
            return False
        response = jwt.decode(req.headers["Authorization"].replace("Bearer ", ""), database.get_setting('jwtToken'),
                              algorithm='HS256', verifyExp=False)
        if response["permission"] == "*":
            return True
        if permissionsRequired.count(":") == 1:
            if "(" + permissionsRequired + ")" in response["permission"]:
                return True
            elif "(" + permissionsRequired.split(":")[0] + ":*)" in response["permission"]:
                return True
        return False
    except Exception:
        return False


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
def login_page():
    return make_response(send_file("web/login.html"))


@app.route('/admin', methods=['GET'])
def admin():
    return make_response(send_file("web/admin.html"))


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
                    "commit_mail": None if database.get_setting(
                        "show-commit-mail") == "false" else participant.get_commit_mail(),
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


@app.route('/api/participants/<string:username>', methods=['POST', 'DELETE'])
@app.route('/api/participants', methods=['GET'], defaults={"username": None})
def participants(username):
    if verify_jwt(request, "participantList:" + request.method):
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


@app.route('/api/setting/<string:settingName>', methods=['GET', 'PUT'])
def setting(settingName):
    # Allow access only with login, or to dark mode variable Prevent access to jwt Variable
    if (verify_jwt(request, "setting:" + request.method) \
            or (settingName == "dark-mode-default" and request.method == 'GET')) and settingName != "jwtToken":
        if request.method == 'PUT':
            if 'value' in request.json:
                value = request.json['value']
                if not re.search(validSettingValues[settingName], value):
                    resp = make_response(json.dumps({"error": "Value not valid"}))
                    resp.headers['Content-Type'] = 'application/json'
                    resp.status_code = 400
                    return resp
                database.set_setting(settingName, value)
        resp = make_response(json.dumps({"name": settingName, "value": database.get_setting(settingName)}))
        resp.headers['Content-Type'] = 'application/json'
        return resp
    else:
        resp = make_response(json.dumps({"error": "Login not found"}))
        resp.headers['Content-Type'] = 'application/json'
        resp.status_code = 403
        return resp


@app.route('/api/users/<string:username>', methods=['POST', 'PUT', 'GET'])
@app.route('/api/users', methods=['GET'], defaults={"username": None})
def getUser(username):
    if request.method == 'GET':
        if username is None and verify_jwt(request, "listUser"):
            resp = make_response(json.dumps(database.get_users_names()))
            resp.headers['Content-Type'] = 'application/json'
            return resp
        elif verify_jwt(request, "showUserInformation:" + username):
            pass
        else:
            return returnError(403, "Not allowed!")
    elif request.method == 'POST':
        if verify_jwt(request, "addUser"):
            pass
        else:
            return returnError(403, "You are not allowed to add a user!")
    elif request.method == 'PUT':
        if request.json is None:
            return returnError(400, "Json Body not found!")
        if 'password' in request.json and verify_jwt(request, "userEdit_password:" + username):
            database.set_user_attribute(username, "password", sha256(request.json['password'].encode()).hexdigest())
        resp = make_response(json.dumps({"message": "Requested!"}))
        resp.headers['Content-Type'] = 'application/json'
        return resp
    else:
        return returnError(404, "Not found!")


@app.route('/api/login', methods=['POST'])
def login():
    if request.json is None or 'username' not in request.json or 'password' not in request.json:
        return returnError(403, "Need username and password")
    user = database.return_user_with_name_and_password(request.json['username'],
                                                       sha256(request.json['password'].encode()).hexdigest())
    if not user:
        return returnError(403, "User not found")
    token = jwt.encode({"username": user[0], "permission": user[2], "issued": time.time()},
                       database.get_setting('jwtToken'), algorithm='HS256')
    resp = make_response(json.dumps({"token": token.decode()}))
    resp.headers['Content-Type'] = 'application/json'
    resp.status_code = 200
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
