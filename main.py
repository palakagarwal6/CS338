import mysql.connector
from mysql.connector import OperationalError
import os
import getpass
cwd = os.getcwd()
scripts = cwd + "\\scripts\\"

def executeSQL(filename):
    # Open and read the file
    fd = open(filename, 'r')
    sqlScript = fd.read()
    fd.close()

    # all SQL commands (split on ';')
    sqlCommands = sqlScript.split(';')

    # Execute every command from the input file
    for command in sqlCommands:
        # skip and print commands that fail
        try:
            c.execute(command)
        except OperationalError as msg:
            print("Command skipped: ", msg)

# sample search function
def searchTitle():
    search = input("Input search Query:")

    search = "'%" + search + "%'"
    query = "SELECT p.Title, p.Release_Date, p.Netflix_Exclusive, r.Rank_As_Of, r.Date_As_Of FROM production as p JOIN rating as r ON p.Title = r.Title Where p.Title LIKE " + search
    c.execute(query)
    result = c.fetchall()
    print("Title, Release Date, Netflix exclusive?, Rank, Rank As of")
    for row in result:
        print(row)


username = input("Enter DB Username: ")
#pw = input("Enter DB Password:")
pw = getpass.getpass(prompt="Enter DB Password: ")

# connect to sql
netflixdb = mysql.connector.connect(
  host="localhost",
  user=username,
  password=pw,
  allow_local_infile=True
)

# connect cursor to db to execute queries
c = netflixdb.cursor()

# create db if does not exist
c.execute("DROP DATABASE IF EXISTS netflix")
c.execute("CREATE DATABASE IF NOT EXISTS netflix")

# create tables
executeSQL(scripts + 'Create Tables.sql')

exec(open(scripts + "split_data.py").read())

# load data
executeSQL(scripts + 'load_data.sql')
netflixdb.commit()

# sample homescreen function
while True:
    print("1: Search Titles")
    print("2: Exit")
    user = input("Select option (1/[2]):")
    if user == "1":
        searchTitle()
    else:
        break