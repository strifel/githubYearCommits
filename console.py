import CommitConnection
username = input("User: ")
year = input("Year: ")
print(CommitConnection.CommitConnection.getCommitsInYear(year, username))
