# CS338 - Group 18 

Through this project, we are aiming to work with a sample database to simulate the Netflix daily top 10 dataset using MySQL on the school server. The database in file "netflix daily top .csv" contains data on the top movies and TV shows in the United States during the COVID-19 pandemic, from April 2020 - March 2022. Users will be able to query, add, and modify data through a Python-based command-line interface (CLI).

# Dependencies

In order to use this project effectively, the user must have:
1. MySQL installed on the school server
2. Any version of Python 3 installed on their machine
3. MySQL connector installed with Python -> use command 'pip install mysql-connector-python'
4. Pandas library installed for Python -> use command 'pip install pandas'.

Once the user has connected the MySQL server using the MySQL command-line client or any MySQL GUI tool, run the following SQL command to create a database:
CREATE DATABASE netflix_db;
USE netflix_db;

# Importing via queries

Now to create a sample table, run the following SQL command:
CREATE TABLE IF NOT EXISTS `netflix_daily_top_sample` (
    `as_of` DATE,
    `rank` INT,
    `year_to_date_rank` VARCHAR(255),
    `last_week_rank` VARCHAR(255),
    `title` VARCHAR(255),
    `type` VARCHAR(255),
    `netflix_exclusive` VARCHAR(255),
    `netflix_release_date` DATE,
    `days_in_top_10` INT,
    `viewership_score` INT

Create a CSV file titled 'netflix_daily_top_sample.csv' with the following sample data and add to the same directory as your Python file:
As of,Rank,Year to Date Rank,Last Week Rank,Title,Type,Netflix Exclusive,Netflix Release Date,Days In Top 10,Viewership Score
2021-01-01,1,,2,Example Movie,Movie,Yes,2021-01-01,30,100
2021-01-01,2,,3,Example TV Show,TV Show,No,2020-12-15,45,95

In your 'config.py' file add the database connection details:
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'your_mysql_password'  # your MySQL password
DB_NAME = 'netflix_db'

Finally, run the load_data.py file where you must replace the csv file name with the name of your sample file or any other file that you are choosing to work with. Upon using the following command:

python load_data.py

You will be able create the table as you require and print it in your console!

# Importing via MySQL Workbench "`Table Data Import Wizard"

1. Create a dummy schema in MySQL Workbench
2. Right Click on the `Tables` in the navigator, and select `Table Data Import Wizard`
3. Download and select the `netflix_daily_top_sample.csv` file from this repo, and press next
4. Select `Create new table` under the schema, and press next
5. The columns should auto-populate, and press next
6. Press next to execute the import
7. If all went well, the data should be imported as a new table
