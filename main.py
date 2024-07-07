import mysql.connector
from mysql.connector import OperationalError
import os
from getpass4 import getpass
import shutil
import time
from tabulate import tabulate
from datetime import datetime

# -----------------------------------
# Utility Functions
# -----------------------------------
cwd = os.getcwd() # get working directory
scripts = cwd + "\\scripts\\" # get scripts directory
max_length = 30

def cut_and_wrap(text):
        if len(text) > max_length:
            return '\n'.join(text[:max_length].split(' ')[:-1]) + "..."
        else:
            return text

# run external sql scripts
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

# clears terminals for CLI purposes
def clear_terminal():
    # Check if the system is Windows or Unix/Linux/Mac
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

# copy prod/sample tables to correct directory for db loading
def copy_files(src_dir, dest_dir):
    for filename in os.listdir(src_dir):
        src_file = os.path.join(src_dir, filename)
        dest_file = os.path.join(dest_dir, filename)

        if os.path.isfile(src_file):
            shutil.copy(src_file, dest_file)

def paginate(data, page_size):
    total_rows = len(data)
    for start in range(0, total_rows, page_size):
        end = min(start + page_size, total_rows)
        page = data[start:end]
        print(tabulate(page, headers="firstrow", tablefmt="grid"))
        if end < total_rows:
            #input("Press Enter to continue...")
            print("next page")

# rebuild database
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
        executeSQL(scripts + 'Create Tables v4.sql')


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
        executeSQL(scripts + 'load_data v3.sql')
        netflixdb.commit()

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f"Done! Time taken: {execution_time:.6f} seconds")

# tabulates result, a resulting sql query
def print_table(table_data):
    table_headers = [col[0] for col in c.description]
    table_data = list(map(cut_and_wrap, table_data))

    formatted_table = tabulate(table_data, headers=table_headers, tablefmt="grid")
    print(formatted_table)



# -----------------------------------
# R6 Functions
# -----------------------------------

# sample search function. Returns movie ID in a table
def search_title():
    search = input("Input search Query:")
    search = "'%" + search + "%'"
    query = "SELECT title, movie_id from movie where title like " + search
    c.execute(query)
    result = c.fetchall()

    print_table(result)

# takes string and prints new lines if string is too long
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


# genre dictionary for searching genres
genre_dict = {
    1: "Adventure",
    2: "Fantasy",
    3: "Animation",
    4: "Drama",
    5: "Horror",
    6: "Action",
    7: "Comedy",
    8: "History",
    9: "Western",
    10: "Thriller",
    11: "Crime",
    12: "Documentary",
    13: "Science Fiction",
    14: "Mystery",
    15: "Music",
    16: "Romance",
    17: "Family",
    18: "War",
    19: "Foreign",
    20: "TV Movie"
}

genre_list = list(genre_dict.items()) # Convert the dictionary to a list of tuples

# Split the list into two halves
half = len(genre_list) // 2
first_half = genre_list[:half]
second_half = genre_list[half:]

# Make the halves the same length by adding empty entries if needed
if len(first_half) > len(second_half):
    second_half.append((None, None))

# Combine the halves side by side
combined_list = []
for (id1, name1), (id2, name2) in zip(first_half, second_half):
    combined_list.append([id1, name1, id2, name2])

genre_list_print = tabulate(combined_list, headers=["Genre ID", "Genre Name", "Genre ID", "Genre Name"], tablefmt="grid") # Print the table

# search movies with specific genres
def select_genre(genre_numbers_str, genre_dict):
    # Check if the input string is empty
    if not genre_numbers_str.strip():
        return []

    # Split the input string by commas and strip any extra spaces
    genre_numbers = [int(num.strip()) for num in genre_numbers_str.split(',')]

    # Look up the genre names using the genre_dict
    genre_names = [genre_dict[num] for num in genre_numbers if num in genre_dict]
    
    return genre_names

def format_genre_query(genre_names):
    # Join the genre names into a single string formatted for SQL
    return ', '.join(f"'{genre}'" for genre in genre_names)

# main genre search function
def search_genre():
    print(genre_list_print)
    print("Select the following genres you would like to search (search multiple, separated by commas:")
    print("Example: 6,9 --> action, western")
    genres = input("Selection:")

    genre_names = select_genre(genres, genre_dict)
    formated_genres = format_genre_query(genre_names)

    if not formated_genres:
        print("Invalid entry detected (most likely genre ID not found)")
        return

    print("Movies with genres:" + formated_genres)
    query = '''
        SELECT DISTINCT m.title , m.vote_average
        FROM movie m 
        JOIN Classified_In c ON m.movie_id = c.movie_id
        JOIN genre g ON c.genre_id = g.genre_id 
        WHERE g.genre_name IN (''' + formated_genres + ''')
        ORDER BY vote_average
        DESC LIMIT 10;'''
    #c.execute(query, (formated_genres,))
    c.execute(query)
    result = c.fetchall()

    if not result:
        print("No movie(s) found...")
        return

    print_table(result)

def search_credited_person():
    person = input("Search person name:")
    query = '''
        SELECT m.title as 'Featured Title'
        FROM movie m
        JOIN Comprises_Of c ON m.movie_id = c.movie_id
        JOIN credit cr ON c.person_id = cr.person_id
        WHERE cr.name LIKE '%''' + person + '''%';
        '''
    c.execute(query)
    result = c.fetchall()

    if not result:
        print("No movie(s) found...")
        return
    
    print_table(result)

# sample search function. Returns movie ID in a table
def movie_data_simple():
    movie_id = input("Input movie ID:")

    query = '''
        SELECT title as Title, vote_average as "Average Rating", status as Status, runtime as "Runtime (Minutes)", adult as "R Rated?", vote_average as "Avg. Rating", vote_count as "Rating count"
        from movie 
        where movie_id = %s'''
    c.execute(query, (movie_id,))
    result = c.fetchall()

    if not result:
        print("No movie found...")
        return

    #print(result)

    print_table(result)

    # print summary
    query = "SELECT overview from movie where movie_id = %s"
    c.execute(query, (movie_id,))
    summary = c.fetchall()
    summary = summary[0]
    summary = summary[0]

    print_summary(summary)

# print genre, production and cast info
def move_data_full():
    movie_id = input("Input movie ID:")

    #queries
    test_query = '''
        SELECT *
        FROM movie m
        WHERE m.movie_id = %s
    '''
    genre_query = '''
        SELECT g.genre_name AS Genre
        FROM Genre g 
        JOIN Classified_In c ON g.genre_id = c.genre_id 
        JOIN movie m ON c.movie_id = m.movie_id 
        WHERE m.movie_id = %s
        '''
    production_query = '''
        SELECT p.production_name AS Productions 
        FROM Production p 
        JOIN Produced_By p1 ON p1.production_id = p.production_id 
        JOIN movie m ON p1.movie_id = m.movie_id 
        WHERE m.movie_id = %s
        '''
    credits_query = '''
        SELECT cr.name AS Name, GROUP_CONCAT(cc.character SEPARATOR ', ') as Characters, NULL AS Roles
        FROM movie m
        JOIN comprises_of co ON m.movie_id = co.movie_id
        JOIN credit cr ON co.person_id = cr.person_id
        JOIN cast cc ON cr.person_id = cc.person_id AND m.movie_id = cc.movie_id
        WHERE m.movie_id = %s
        GROUP BY cr.name

        UNION

        SELECT cr.name AS Name, NULL AS Characters, GROUP_CONCAT(p.Job_Name SEPARATOR ', ') as Roles
        FROM movie m
        JOIN comprises_of co ON m.movie_id = co.movie_id
        JOIN credit cr ON co.person_id = cr.person_id
        JOIN performs p ON cr.person_id = p.person_id AND m.movie_id = p.movie_id
        WHERE m.movie_id = %s
        GROUP BY cr.name

        '''
    
    c.execute(test_query, (movie_id,))
    test_result = c.fetchall()

    if not test_result:
        print("Movie not found...")
        return

    c.execute(genre_query, (movie_id,))
    genre_result = c.fetchall()

    print_table(genre_result)

    c.execute(production_query, (movie_id,))
    prod_result = c.fetchall()

    print_table(prod_result)

    c.execute(credits_query, (movie_id, movie_id))
    creds_result = c.fetchall()

    table_headers = [col[0] for col in c.description]
    table_data = creds_result

    #print(credits_table)
    paginate(table_data, 20)

    return

# -----------------------------------
# R7 Functions
# -----------------------------------

def search_production():
    production = input("Input production Query:")
    query = '''
        SELECT m.movie_id, m.title, p.production_name
        FROM movie m
        JOIN Produced_By c ON m.movie_id = c.movie_id
        JOIN Production p ON c.production_id = p.production_id
        WHERE production_name LIKE '%'''+ production + '''%'
        ORDER BY p.production_name, m.movie_id, m.release_date DESC;
        '''
    c.execute(query)
    result = c.fetchall()

    if not result:
        print("No Movie(s) found...")
        return

    print_table(result)

# -----------------------------------
# R8 Functions
# -----------------------------------

def update_movie():
    # get movie id to edit
    movie_id = input("Input movie ID:")
    query = '''
        SELECT movie_id, title, status, release_date, adult, video, runtime
        from movie 
        where movie_id = %s
        '''
    c.execute(query, (movie_id,))
    result = c.fetchall()

    # quit if no movie found
    if not result:
        print("Movie not found...")
        return

    print_table(result)

    # print summary
    query = "SELECT overview from movie where movie_id = %s"
    c.execute(query, (movie_id,))
    summary = c.fetchall()
    summary = summary[0]
    summary = summary[0]

    print_summary(summary)

    # print update options
    print("1: Movie ID")
    print("2: Title")
    print("3: Overview")
    print("4: Status")
    print("5: Release Date")
    print("6: Adult")
    print("7: video")
    print("8: Runtime")
    print("9: Exit to previous menu")
    user = input("Select movie_attribute to edit (Default 9): ")

    #movie id
    if user == "1":
        print("Type nothing and press enter to cancel")
        new_movie_id = input("Input new movie ID (non-negative int): ")
        if not new_movie_id.strip():
            clear_terminal()
            return

        # check if new movie id is non-negative int
        if not new_movie_id.isdigit() or new_movie_id.isdigit() < 0:
            print("Invalid input, must be non-negative integer")
            return
        
        # check if new movie_id already exists as a movie
        check_unique_id = '''
            SELECT *
            FROM movie
            where id = %s
            '''
        c.execute(query, (new_movie_id,))
        check_result = c.fetchall()

        if check_result:
            print("Movie ID already exists")
            return

        query = '''
            UPDATE movie
            SET movie_id = %s
            WHERE movie_id = %s
            '''
        c.execute(query, (new_movie_id,movie_id))
        netflixdb.commit()
        clear_terminal()
        print("successful!")

    #title
    elif user == "2":
        print("Type nothing and press enter to cancel")
        new_title = input("Input new movie title: ")
        if not new_title.strip():
            clear_terminal()
            return
        
        query = '''
            UPDATE movie
            set title = %s
            WHERE movie_id = %s
            '''
        c.execute(query, (new_title,movie_id))
        netflixdb.commit()
        clear_terminal()
        print("successful!")
        
    #Overview
    elif user == "3":
        print("Type nothing and press enter to cancel")
        new_overview = input("Input new overview: ")
        if not new_overview.strip():
            clear_terminal()
            return
        
        query = '''
            UPDATE movie
            set overview = %s
            WHERE movie_id = %s
            '''
        c.execute(query, (new_overview,movie_id))
        netflixdb.commit()
        clear_terminal()
        print("successful!")

    #Status
    elif user == "4":
        options = {
            1: "Rumored",
            2: "Planned",
            3: "In Production",
            4: "Post Production",
            5: "Released",
            6: "Canceled",
            7: "Exit",
        }

        print("1: Rumored")
        print("2: Planned")
        print("3: In Production")
        print("4: Post Production")
        print("5: Released")
        print("6: Canceled")
        print("7: Exit")
        
        new_status = input("Select new overview (default 7): ")
        try:
            choice = int(new_status)
            if choice in options:
                new_status = options[choice]
            else:
                print("Invalid input, exiting...")
                clear_terminal()
                return
        except ValueError:
            print("Invalid input, exiting...")
            clear_terminal()
            return

        
        query = '''
            UPDATE movie
            set status = %s
            WHERE movie_id = %s
            '''
        c.execute(query, (new_status,movie_id))
        netflixdb.commit()
        clear_terminal()
        print("successful!")

    # release date
    elif user == "5":
        print("Type nothing and press enter to cancel")
        new_date = input("Input new overview (yyyy-mm-dd format): ")
        if not new_date.strip():
            clear_terminal()
            return
        
        try:
            datetime.strptime(new_date, "%Y-%m-%d")
            print("Valid Date")
        except ValueError:
            print("Invalid date format, exiting...")
            clear_terminal()
            return
        
        query = '''
            UPDATE movie
            set release_date = %s
            WHERE movie_id = %s
            '''
        c.execute(query, (new_date,movie_id))
        netflixdb.commit()
        clear_terminal()
        print("successful!")

    #Adult
    elif user == "6":
        options = {
            1: "True",
            2: "False",
            3: "Exit",
        }

        print("1: True")
        print("2: False")
        print("3: Exit")
        
        new_adult = input("Select option (default 3): ")
        try:
            choice = int(new_adult)
            if choice in options:
                new_adult = options[choice]
            else:
                print("Invalid input, exiting...")
                clear_terminal()
                return
        except ValueError:
            print("Invalid input, exiting...")
            clear_terminal()
            return
        
        query = '''
            UPDATE movie
            set adult = %s
            WHERE movie_id = %s
            '''
        c.execute(query, (new_adult,movie_id))
        netflixdb.commit()
        clear_terminal()
        print("successful!")

    #video
    elif user == "7":
        options = {
            1: "True",
            2: "False",
            3: "Exit",
        }

        print("1: True")
        print("2: False")
        print("3: Exit")
        
        new_video = input("Select option (default 3): ")
        try:
            choice = int(new_video)
            if choice in options:
                new_video = options[choice]
            else:
                print("Invalid input, exiting...")
                clear_terminal()
                return
        except ValueError:
            print("Invalid input, exiting...")
            clear_terminal()
            return
        
        query = '''
            UPDATE movie
            set video = %s
            WHERE movie_id = %s
            '''
        c.execute(query, (new_video,movie_id))
        netflixdb.commit()
        clear_terminal()
        print("successful!")

    #runtime
    elif user == "8":
        print("Type nothing and press enter to cancel")
        new_runtime = input("Input new runtime, in minutes (non-negative int): ")
        if not new_runtime.strip():
            clear_terminal()
            return

        # check if new movie id is non-negative int
        if not new_runtime.isdigit() or new_runtime.isdigit() < 0:
            print("Invalid input, must be non-negative integer")
            return

        query = '''
            UPDATE movie
            SET runtime = %s
            WHERE movie_id = %s
            '''
        c.execute(query, (new_runtime,movie_id))
        netflixdb.commit()
        clear_terminal()
        print("successful!")
    else:
        return

# -----------------------------------
# R11 Functions
# -----------------------------------

def genre_count():
    query = '''
        SELECT g.genre_name as Genre, COUNT(*) AS "Movie Count" 
        FROM genre g
        JOIN Classified_In c ON g.genre_id = c.genre_id 
        GROUP BY g.genre_name 
        ORDER BY movie_count DESC
        LIMIT 10
        '''
    c.execute(query)
    result = c.fetchall()
    print_table(result)

def best_genre():
    query = '''
        SELECT g.genre_name as Genre, ROUND(AVG(m.vote_average), 2) AS "Avg. Rating"
        FROM genre g JOIN Classified_In c ON g.genre_id = c.genre_id
        JOIN movie m ON c.movie_id = m.movie_id
        GROUP BY g.genre_name
        ORDER BY average_rating DESC;
        '''
    c.execute(query)
    result = c.fetchall()
    print_table(result)

# -----------------------------------
# Connecting to DB
# -----------------------------------

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

# -----------------------------------
# Menu Nav
# -----------------------------------

def R6():
    clear_terminal()
    while True:
        print("1: Search titles, fuzzy")
        print("2: Search titles with genre")
        print("3: Search featuring person, fuzzy")
        print("4: Basic details and synopsis (from movie ID)")
        print("5 (R12): Search Metadata (from movie ID)")
        print("6: Exit to main menu")
        user = input("Select option (default 6): ")
        if user == "1":
            search_title()
        elif user == "2":
            search_genre()
        elif user == "3":
            search_credited_person()
            #print("to be implemented")
        elif user == "4":
            movie_data_simple()
        elif user == "5":
            move_data_full()
            #print("to be implemented")
        else:
            return

def R7():
    clear_terminal()
    while True:
        print("1: Search movies produced by production, fuzzy")
        print("2: Exit to main menu")
        user = input("Select option (default 2): ")
        if user == "1":
            search_production()
        else:
            return

def R8():
    clear_terminal()
    while True:
        print("1: Update movie attributes")
        print("2: Exit to main menu")
        user = input("Select option (default 2): ")

        if user == "1":
            update_movie()
        else:
            return

def R11():
    while True:
        print("1: Popular Genres")
        print("2: Most successful Genres")
        print("3: Exit to previous menu")
        user = input("Select option (Default 3): ")

        if user == "1":
            genre_count()
        elif user == "2":
            best_genre()
        else:
            clear_terminal()
            return

# main menu
def menu():
    while True:
        clear_terminal()
        print("1 (R6): Searching and metadata")
        print("2 (R7): search productions")
        print("3 (R8): Edit Movie Details")
        print("4 (R11): Get statistics")
        print("5: Remake database")
        print("6: Exit")
        user = input("Select option (default 6): ")
        if user == "1":
            R6()
        elif user == "2":
            R7()
        elif user == "3":
            R8()
        elif user == "4":
            R11()
        elif user == "5":
            redo_database()
        else:
            break

c.execute("Use Netflix")
menu()
netflixdb.close()