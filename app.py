from flask import Flask
from flask import render_template
from flask import make_response
from ConnectionManager import CommitConnection
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


if __name__ == '__main__':
    app.run()
