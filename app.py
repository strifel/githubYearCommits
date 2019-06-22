from flask import render_template, make_response, send_from_directory, request, Flask
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
    year = datetime.now().strftime("%Y")
    if (reload and (DatabaseController.get_setting("allow-force") == "true" or
                    request.cookies.get("gyc_login") == DatabaseController.getPassword())) or \
            datetime.now().timestamp() - timeUpdated > DatabaseController.get_setting("cache"):
        users = list()
        timeUpdated = datetime.now().timestamp()
        user_contributions = {}
        for user in DatabaseController.get_user():
            user_contributions.update({user[0]: CommitConnection.getCommitsInYear(year, user[0])})
        sorted_contributions = sorted(user_contributions.items(), key=operator.itemgetter(1), reverse=True)
        for user in sorted_contributions:
            users.append({"name": user[0], "contributions": user[1]})

    # users.append({"name": user[0], "contributions": CommitConnection.getCommitsInYear(year, user[0])})
    # users.append(
    # users.append({"name": "robmroi03", "contributions": CommitConnection.getCommitsInYear(year, "robmroi03")})
    #    {"name": "felixletsplayyt", "contributions": CommitConnection.getCommitsInYear(year, "felixletsplayyt")})
    resp = make_response(render_template("index.html.twig", users=users, time=datetime.fromtimestamp(timeUpdated)
                                         .strftime('%H:%M:%S'), year=year))
    resp.headers['Cache-Control'] = "no-cache, no-store, must-revalidate"
    resp.headers['Pragma'] = "no-cache"
    resp.headers['Expires'] = "0"
    return resp


@app.route('/login', methods=['GET'])
@app.route('/backend', methods=['GET', 'POST'])
def backend():
    if request.method == "GET":
        if request.cookies.get("gyc_login") == DatabaseController.getPassword():
            resp = make_response(render_template("backend.html.twig", users=DatabaseController.get_user()))
            return resp
        else:
            resp = make_response(render_template("login.html.twig"))
            resp.delete_cookie("gyc_login")
            return resp
    else:
        if request.cookies.get("gyc_login") == DatabaseController.getPassword():
            if request.form.get("delete") is not None:
                DatabaseController.remove_user(request.form.get("delete"))
            if request.form.get("username") is not None:
                DatabaseController.add_user(request.form.get("username"))
            if request.form.get("setting") is not None:
                if request.form.get("setting") == "password":
                    hashed = sha256(request.form.get("value").encode()).hexdigest()
                    DatabaseController.set_setting("password", hashed)
                else:
                    DatabaseController.set_setting(request.form.get("setting"), request.form.get("value"))
            return '<html><head><meta http-equiv="refresh" content="0; url=/login" /></head></html>'


@app.route('/user/<string:user>/<int:year>', methods=['GET'])
@app.route('/user/<string:user>', methods=['GET'], defaults={"year": int(datetime.now().strftime("%Y"))})
def user_page(user, year):
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
    # response
    resp = make_response(render_template("user.html.twig", username=user, contributions=CommitConnection
                                         .getCommitsInYear(year, user), year=year, languages=sorted_languages, email=mail))

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
