import mysql.connector
from mysql.connector import OperationalError
import os
from getpass4 import getpass
import shutil
import time
import tabulate

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

def copy_files(src_dir, dest_dir):
    for filename in os.listdir(src_dir):
        src_file = os.path.join(src_dir, filename)
        dest_file = os.path.join(dest_dir, filename)

        if os.path.isfile(src_file):
            shutil.copy(src_file, dest_file)

# sample search function. Returns movie ID in a table
def search_title():
    search = input("Input search Query:")
    search = "'%" + search + "%'"
    query = "SELECT title, movie_id from movie where title like " + search
    c.execute(query)
    result = c.fetchall()

    table_headers = [col[0] for col in c.description]
    table_data = result
    formatted_table = tabulate.tabulate(table_data, headers=table_headers, tablefmt="grid")
    print(formatted_table)

# takes string
def print_summary(summary):
    print("Movie Summary:")
    words = summary.split()
    current_line = ""
    for word in words:
        if len(current_line) + len(word) <= 50:
            current_line += word + " "
        else:
            print(current_line.rstrip())
            current_line = word + " "
    print(current_line.rstrip())
    print("")

# sample search function. Returns movie ID in a table
def movie_data():
    search = input("Input movie ID:")
    search = "'" + search + "'"

    
    query = "SELECT title, movie_id, vote_average, status, runtime from movie where movie_id = " + search
    c.execute(query)
    result = c.fetchall()

    if not result:
        print("No movie found...")
        return

    print(result)

    table_headers = [col[0] for col in c.description]
    table_data = result
    formatted_table = tabulate.tabulate(table_data, headers=table_headers, tablefmt="grid")

    query = "SELECT overview from movie where movie_id = " + search
    c.execute(query)
    summary = c.fetchall()
    summary = summary[0]
    summary = summary[0]

    print(formatted_table)
    print_summary(summary)

def redo_database():
    print("Do you want to rewrite the whole database?")
    print("(you must do this if you haven't created the DB yet)")
    redo = input("y/[n]: ")

    if (redo == "y"):
        print("1: Use sample dataset")
        print("2: Use full prod dataset")
        dbtype = input("([1]/2): ")

        print("remaking database")
        # create db if does not exist
        c.execute("DROP DATABASE IF EXISTS netflix")
        c.execute("CREATE DATABASE IF NOT EXISTS netflix")

        # create tables
        # print("making tables")
        executeSQL(scripts + 'Create Tables v3.sql')


        # COPY DATA TO UPLOADS
        print("copying csv files")
        sqlpath = 'C:\\ProgramData\\MySQL\\MySQL Server 8.4\\Uploads'
        table_src = cwd + "\\tables"

        if dbtype == "2":
            table_src = table_src + "\\prod"
        else:
            table_src = table_src + "\\sample"

        copy_files(table_src, sqlpath)

        print("Loading data into database... (this may take a while)")
        start_time = time.perf_counter()

        # load data
        executeSQL(scripts + 'load_data v2.sql')
        netflixdb.commit()

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f"Done! Time taken: {execution_time:.6f} seconds")

save = ""
username = ""

# grab creds
with open(cwd + "\\scripts\\creds\\user.txt") as f:
    username = f.read()

with open(cwd + "\\scripts\\creds\\pw.txt") as f:
    pw = f.read()

creds_saved = ""

if len(username) == 0 or len(pw) == 0:
    creds_saved = False
    print("No saved credentials found")
else:
    save = input("Found saved credentials, load? ([y]/n): ") 
    if save == "n":
        creds_saved = False
    else:
        creds_saved = True

if not creds_saved:
    username = input("Enter DB Username: ")
    pw = getpass(prompt="Enter DB Password: ")
    print("Do you want to save these credentials for later?")
    save = input("WARNING!! UNSECURE TO SAVE CREDS!! (y/[n]): ")
    if save == "y":
        with open(cwd + "\\scripts\\creds\\user.txt", 'w') as f:
            f.write(username)

        with open(cwd + "\\scripts\\creds\\pw.txt", 'w') as f:
            f.write(pw)

# connect to sql
netflixdb = mysql.connector.connect(
    host="localhost",
    user=username,
    password=pw,
    allow_local_infile=True,
)

# connect cursor to db to execute queries
c = netflixdb.cursor()

redo_database()

# sample homescreen function
while True:
    c.execute("Use Netflix;")
    print("1: Search Titles")
    print("2: Get Movie Details (from ID)")
    print("3: remake database")
    print("4: Exit")
    user = input("Select option (default 4): ")
    if user == "1":
        search_title()
    elif user == "2":
        movie_data()
    elif user == "3":
        redo_database()
    else:
        break

netflixdb.close()