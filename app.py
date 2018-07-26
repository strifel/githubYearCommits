from flask import Flask
from flask import render_template
from CommitConnection import CommitConnection
import datetime

app = Flask(__name__)


@app.route('/', methods=['GET'])
def main_page():
    # TODO get users dynamicaly
    year = datetime.datetime.now().strftime("%Y")
    users = list()
    users.append(
        {"name": "felixletsplayyt", "contributions": CommitConnection.getCommitsInYear(year, "felixletsplayyt")})
    users.append({"name": "robmroi03", "contributions": CommitConnection.getCommitsInYear(year, "robmroi03")})
    return render_template("index.html.twig", users=users)


if __name__ == '__main__':
    app.run()

