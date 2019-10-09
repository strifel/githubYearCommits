import sys
from src.ConnectionManager import DatabaseController
from requests import get


def print_help():
    print("GithubYearCommits cache.py help")
    print("Use cache-rebuild (your sites URL) or cache-clear")
    sys.exit(0)


database = DatabaseController()

if len(sys.argv) >= 2:
    command = sys.argv[1]
    if command == "cache-rebuild":
        if len(sys.argv) != 3:
            print_help()
        url = sys.argv[2]
        if not ((url.startswith("http://") or url.startswith("https://")) and url.endswith("/")):
            print_help()
        result = database.execute_sql("SELECT context FROM cache", [], False)
        database.execute_sql("DELETE FROM cache", [], True)
        for row in result:
            if row[0] == "contributions":
                get(url + "api/contributions")
            elif row[0].startswith("participant:"):
                get(url + "api/participants/" + row[0].split(":")[1])
    elif command == "cache-clear":
        database.execute_sql("DELETE FROM cache", [], True)
    else:
        print_help()
else:
    print_help()
