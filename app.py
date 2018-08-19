from flask import Flask
from flask import render_template
from flask import make_response
from flask import request
from connection.ConnectionManager import CommitConnection
from connection.ConnectionManager import DatabaseController
from datetime import datetime

app = Flask(__name__)
users = list()
timeUpdated = 0


@app.route('/', methods=['GET'])
def main_page():
    global timeUpdated
    year = datetime.now().strftime("%Y")
    if datetime.now().timestamp() - timeUpdated > DatabaseController.get_setting("cache"):
        timeUpdated = datetime.now().timestamp()
        for user in DatabaseController.get_user():
            users.append({"name": user[0], "contributions": CommitConnection.getCommitsInYear(year, user[0])})

    # users.append(
    # users.append({"name": "robmroi03", "contributions": CommitConnection.getCommitsInYear(year, "robmroi03")})
    #    {"name": "felixletsplayyt", "contributions": CommitConnection.getCommitsInYear(year, "felixletsplayyt")})
    resp = make_response(render_template("index.html.twig", users=users, time=datetime.fromtimestamp(timeUpdated)
                                         .strftime('%H:%M:%S')))
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
            return '<html><head><meta http-equiv="refresh" content="0; url=/login" /></head></html>'


if __name__ == '__main__':
    app.run()
