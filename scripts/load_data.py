import mysql.connector
import pandas as pd
from datetime import datetime

df = pd.read_csv('netflix daily top .csv')

df.columns = df.columns.str.strip()

df.rename(columns={
    'As of': 'as_of',
    'Rank': 'rank',
    'Year to Date Rank': 'year_to_date_rank',
    'Last Week Rank': 'last_week_rank',
    'Title': 'title',
    'Type': 'type',
    'Netflix Exclusive': 'netflix_exclusive',
    'Netflix Release Date': 'netflix_release_date',
    'Days In Top 10': 'days_in_top_10',
    'Viewership Score': 'viewership_score'
}, inplace=True)

df['as_of'] = pd.to_datetime(df['as_of'], errors='coerce')
df['netflix_release_date'] = pd.to_datetime(df['netflix_release_date'], errors='coerce').dt.date

df['year_to_date_rank'].fillna('', inplace=True)
df['last_week_rank'].fillna('', inplace=True)
df['title'].fillna('', inplace=True)
df['type'].fillna('', inplace=True)
df['netflix_exclusive'].fillna('', inplace=True)
df['netflix_release_date'].fillna(pd.NaT, inplace=True)
df['days_in_top_10'].fillna(0, inplace=True)
df['viewership_score'].fillna(0, inplace=True)

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='password in here',  # your MySQL password 
        database='netflix_db'
    )
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS `netflix_daily_top`')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS `netflix_daily_top` (
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
        );
    ''')


    for index, row in df.iterrows():
        cursor.execute('''
            INSERT INTO `netflix_daily_top` (
                `as_of`, `rank`, `year_to_date_rank`, `last_week_rank`, `title`, `type`, 
                `netflix_exclusive`, `netflix_release_date`, `days_in_top_10`, `viewership_score`
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            row['as_of'].date() if pd.notnull(row['as_of']) else None,
            row['rank'],
            row['year_to_date_rank'],
            row['last_week_rank'],
            row['title'],
            row['type'],
            row['netflix_exclusive'],
            row['netflix_release_date'] if pd.notnull(row['netflix_release_date']) else None,
            row['days_in_top_10'],
            row['viewership_score']
        ))

    cursor.execute('SELECT * FROM `netflix_daily_top`')
    rows = cursor.fetchall()
    for row in rows:
        print(row)
        
    conn.close()

except mysql.connector.Error as err:
    print(f"Error: {err}")

