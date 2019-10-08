from sqlite3 import IntegrityError
from src.Helper import returnError, returnJSON, returnMessage, returnJSONText
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
from src.Util import sortWithCount
import operator

app = Flask(__name__, static_url_path='')
database = DatabaseController()


def verify_jwt(req, permissionsRequired):
    try:
        if 'Authorization' not in req.headers:
            return False
        response = jwt.decode(req.headers["Authorization"].replace("Bearer ", ""), database.get_setting('jwtToken'),
                              algorithm='HS256')
        if response["permission"] == "*":
            return True
        if permissionsRequired.count(":") == 1:
            if "(" + permissionsRequired + ")" in response["permission"]:
                return True
            elif "(" + permissionsRequired.split(":")[0] + ":*)" in response["permission"]:
                return True
        else:
            return "(" + permissionsRequired + ")" in response["permission"]
    except Exception:
        return False


@app.route('/', methods=['GET'])
def main_page():
    return make_response(send_file("web/index.html"))


@app.route('/api/contributions', methods=['GET'])
def contributions():
    cache = database.get_cache("contributions")
    if not (not cache):
        return returnJSONText(cache)
    duration = database.get_setting("duration")
    pcontributions = {}
    attribute = ""
    if duration == "year":
        attribute = datetime.now().strftime("%Y")
    for participant in database.get_participants():
        if duration == "year":
            pcontributions.update({participant[0]: {"username": participant[0], "count": CommitConnection.getCommitsInYear(attribute, participant[0])}})
        elif duration == "eternity":
            pcontributions.update({participant[0]: {"username": participant[0], "count": CommitConnection.getTotalCommits(participant[0])}})
        else:
            pcontributions.update({participant[0]: {"username": participant[0], "count": 0}})
    pcontributions = sortWithCount(pcontributions)
    response = json.dumps({"participants": pcontributions, "information": {"duration": duration, "attribute": attribute}})
    database.set_cache("contributions", response, int(database.get_setting("cache")))
    return returnJSONText(response)


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
            return returnError(404, "User not found")
    # Checking for cache
    cache = database.get_cache("participant:" + username)
    if not (not cache):
        return returnJSONText(cache)
    # Finding year in query string
    if "contributions_year" in request.args:
        year = int(request.args['contributions_year'])
    else:
        year = int(datetime.now().strftime("%Y"))
    # Create Participant Object and response
    participant = Participant(username)
    resp = json.dumps(
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
        )
    database.set_cache("participant:" + username, resp, database.get_setting("cache"))
    return returnJSONText(resp)


@app.route('/api/participants/<string:username>', methods=['POST', 'DELETE'])
@app.route('/api/participants', methods=['GET'], defaults={"username": None})
def participants(username):
    if verify_jwt(request, "participantList:" + request.method):
        if request.method == 'GET':
            entries = []
            for row in database.get_participants():
                entries.append(row[0])
            return returnJSON(entries)
        elif request.method == 'POST':
            try:
                database.add_participants(username)
            except IntegrityError:
                return returnError(409, "Participant already exists")
            else:
                resp = make_response(json.dumps({"message": "Added participant!"}), 201)
                resp.headers['Content-Type'] = 'application/json'
                return resp
        elif request.method == 'DELETE':
            database.remove_participants(username)
            return returnMessage("Removed participant!")
    else:
        return returnError(403, "You are not authorized!")


@app.route('/api/setting/<string:settingName>', methods=['GET', 'PUT'])
def setting(settingName):
    # Allow access only with login, or to dark mode variable Prevent access to jwt Variable
    if (verify_jwt(request, "setting:" + request.method) \
            or (settingName == "dark-mode-default" and request.method == 'GET')) and settingName != "jwtToken":
        if request.method == 'PUT':
            if 'value' in request.json:
                value = request.json['value']
                if (type(value) is not str) or (settingName not in validSettingValues) or (not re.search(validSettingValues[settingName], value)):
                    return returnError(400, "Not working setting/value pair")
                database.set_setting(settingName, value)
        return returnJSON({"name": settingName, "value": database.get_setting(settingName)})
    else:
        return returnError(403, "There was a login error")


@app.route('/api/users/<string:username>', methods=['PUT', 'GET', 'DELETE'])
@app.route('/api/users', methods=['GET', 'POST'], defaults={"username": None})
def user(username):
    if request.method == 'GET':
        if username is None and verify_jwt(request, "listUser"):
            resp = make_response(json.dumps(database.get_users_names()))
            resp.headers['Content-Type'] = 'application/json'
            return resp
        elif username is not None and verify_jwt(request, "showUserInformation:" + username):
            user = database.get_user_by_name(username)
            if user is None:
                return returnError(404, "User does not exists")
            return returnJSON({"username": user[0], "permissions": user[2]})
        else:
            return returnError(403, "Not allowed!")
    elif request.method == 'POST':
        if verify_jwt(request, "addUser"):
            if request.json is None or \
                    (('username' not in request.json) or (type(request.json['username']) != str)) or \
                    ('password' not in request.json) or (type(request.json['password']) != str) or \
                    ('permissions' not in request.json) or (type(request.json['permissions']) != str):
                return returnError(400, "The request must be JSON and must contain username, password and permissions")
            try:
                database.create_user(request.json['username'], sha256(request.json['password'].encode()).hexdigest(),
                                     request.json['permissions'])
            except IntegrityError:
                return returnError(409, "User already exists")
            return returnMessage("User added!")
        else:
            return returnError(403, "You are not allowed to add a user!")
    elif request.method == 'PUT':
        if request.json is None:
            return returnError(400, "Json Body not found!")
        if 'password' in request.json and type(request.json['password']) is str and verify_jwt(request, "userEdit_password:" + username):
            database.set_user_attribute(username, "password", sha256(request.json['password'].encode()).hexdigest())
        if 'permissions' in request.json and type(request.json['permissions']) is str and verify_jwt(request, "user:permissions"):
            database.set_user_attribute(username, "permission", request.json['permissions'])
        return returnMessage("Okay!")
    elif request.method == 'DELETE':
        if verify_jwt(request, "deleteUser"):
            database.delete_user(username)
            return returnMessage("Deleted user!")
        else:
            return returnError(403, "You do not have the permission to delete a user")
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
    exp = int(time.time() + (60 * 15))
    token = jwt.encode({"username": user[0], "permission": user[2], "iat": int(time.time()), "exp": exp},
                       database.get_setting('jwtToken'), algorithm='HS256')
    return returnJSON({"token": token.decode(), "exp": exp})


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
