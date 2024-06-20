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

# sample search function
def searchTitle():
    search = input("Input search Query:")
    search = "'%" + search + "%'"
    query = "SELECT title, status, release_date, runtime, vote_average from movie where title like " + search
    c.execute(query)
    result = c.fetchall()
    #print("title, status, release_date, runtime, vote_average")
    #for row in result:
    #    print(row)

    table_headers = [col[0] for col in c.description]
    table_data = result
    formatted_table = tabulate.tabulate(table_data, headers=table_headers, tablefmt="grid")
    print(formatted_table)


def copy_files(src_dir, dest_dir):
    for filename in os.listdir(src_dir):
        src_file = os.path.join(src_dir, filename)
        dest_file = os.path.join(dest_dir, filename)

        if os.path.isfile(src_file):
            shutil.copy(src_file, dest_file)
            #print(f"Copied: {src_file} to {dest_file}")


username = input("Enter DB Username: ")
pw = getpass(prompt="Enter DB Password: ")

# connect to sql
netflixdb = mysql.connector.connect(
    host="localhost",
    user=username,
    password=pw,

    #user="root",
    #password="baked in password",

    allow_local_infile=True,
)

# connect cursor to db to execute queries
c = netflixdb.cursor()

print("Do you want to rewrite the whole database?")
print("(you must do this if you haven't created the DB yet)")
redo = input("y/[n]: ")

if (redo == "y"):
    # create db if does not exist
    c.execute("DROP DATABASE IF EXISTS netflix")
    c.execute("CREATE DATABASE IF NOT EXISTS netflix")

    # create tables
    executeSQL(scripts + 'Create Tables v3.sql')


    # COPY DATA TO UPLOADS
    sqlpath = 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads'
    table_src = cwd + "\\tables"
    copy_files(table_src, sqlpath)

    print("Loading data into database... (this will take a while)")
    start_time = time.perf_counter()

    # load data
    executeSQL(scripts + 'load_data v2.sql')
    netflixdb.commit()

    end_time = time.perf_counter()
    execution_time = end_time - start_time
    print(f"Done! Time taken: {execution_time:.6f} seconds")

# sample homescreen function
while True:
    c.execute("Use Netflix;")
    print("1: Search Titles")
    print("2: Exit")
    user = input("Select option (1/[2]):")
    if user == "1":
        searchTitle()
    else:
        break

netflixdb.close()