from flask import Flask
from flask import render_template
from flask import make_response
from flask import request
from connection.ConnectionManager import CommitConnection
from connection.ConnectionManager import DatabaseController
from datetime import datetime

app = Flask(__name__)


@app.route('/', methods=['GET'])
def main_page():
    # TODO get users dynamicaly
    year = datetime.now().strftime("%Y")
    users = list()
    users.append(
        {"name": "felixletsplayyt", "contributions": CommitConnection.getCommitsInYear(year, "felixletsplayyt")})
    users.append({"name": "robmroi03", "contributions": CommitConnection.getCommitsInYear(year, "robmroi03")})
    resp = make_response(render_template("index.html.twig", users=users, time=datetime.now().strftime('%H:%M:%S')))
    resp.headers['Cache-Control'] = "no-cache, no-store, must-revalidate"
    resp.headers['Pragma'] = "no-cache"
    resp.headers['Expires'] = "0"
    return resp


@app.route('/backend', methods=['GET', 'POST'])
def backend():
    if request.method == "GET":
        if request.cookies.get("gyc_login") == DatabaseController.getPassword():
            resp = make_response(render_template("backend.html.twig"))
            return resp
        else:
            resp = make_response(render_template("login.html.twig"))
            resp.delete_cookie("gyc_login")
            return resp
    else:
        if request.cookies.get("gyc_login") == DatabaseController.getPassword():
            if request.form.get("delete") != "":
                DatabaseController.remove_user(request.form.get("delete"))
            if request.form.get("username") != "":
                DatabaseController.add_user(request.form.get("username"))
            return "<body onload='location.reload(true);'></body>"


if __name__ == '__main__':
    app.run()
