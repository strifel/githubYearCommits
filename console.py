import ConnectionManager
username = input("User: ")
year = input("Year: ")
print(ConnectionManager.CommitConnection.getCommitsInYear(year, username))
