import pandas as pd
import streamlit as st
import mysql.connector
from mysql.connector import MySQLConnection

GLOBAL_CNX = None


def connect_to_mysql() -> MySQLConnection:
    global GLOBAL_CNX

    config = {
        "host": "localhost",
        "user": "root",
        "password": "password"
    }

    if GLOBAL_CNX:
        return GLOBAL_CNX
    else:
        GLOBAL_CNX = mysql.connector.connect(**config)
        return GLOBAL_CNX


def create_database_if_not_exists(cnx: MySQLConnection, db_name: str) -> None:
    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")


def use_database(cnx: MySQLConnection, db_name: str) -> None:
    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            cursor.execute(f"USE {db_name}")


def create_movies_table(cnx: MySQLConnection) -> bool:
    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            query = """
            CREATE TABLE IF NOT EXISTS movies(
                movie_id INT PRIMARY KEY,
                title VARCHAR(255),
                overview TEXT,
                status VARCHAR(50),
                release_date DATE,
                adult BOOLEAN,
                video BOOLEAN,
                runtime INT,
                vote_average FLOAT,
                vote_count INT
            )
            """
            cursor.execute(query)


def check_movies_table_exists(cnx: MySQLConnection) -> bool:
    with cnx.cursor() as cursor:
        cursor.execute(f"SHOW TABLES LIKE 'movies'")
        result = cursor.fetchone()
        movies_table_exists = result is not None
        return movies_table_exists


def populate_movies_table(cnx: MySQLConnection, csv_file_path: str) -> None:
    df = pd.read_csv(csv_file_path)

    df = df.astype({
        'movie_id': int,
        'title': str,
        'overview': str,
        'status': str,
        'adult': bool,
        'runtime': int,
        'vote_average': float,
        'vote_count': int
    })

    for _, row in df.iterrows():
        query = """
        INSERT INTO movies(movie_id, title, overview, status, release_date, adult, video, runtime, vote_average, vote_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = tuple(row)

        if cnx and cnx.is_connected():
            with cnx.cursor() as cursor:
                cursor.execute(query, values)


def load_all_movies_from_db(cnx: MySQLConnection) -> pd.DataFrame:
    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            query = "SELECT * FROM movies"
            df = pd.read_sql(query, cnx)
            return df


def update_movie_details_in_db(cnx: MySQLConnection, row: pd.Series) -> None:
    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            query = """
            UPDATE movies
            SET 
                title = %s,
                overview = %s,
                status = %s,
                release_date = %s,
                adult = %s,
                video = %s,
                runtime = %s,
                vote_average = %s,
                vote_count = %s
            WHERE 
                movie_id = %s
            """

            values = (
                str(row['title']),
                str(row['overview']),
                str(row['status']),
                row['release_date'].strftime('%Y-%m-%d'),
                bool(row['adult']),
                bool(row['video']),
                int(row['runtime']),
                float(row['vote_average']),
                int(row['vote_count']),
                int(row['movie_id'])
            )
            cursor.execute(query, values)


def delete_movie_from_db(cnx: MySQLConnection, movie_id: int) -> None:
    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            movie_id = int(movie_id)
            cursor.execute(
                "DELETE FROM movies WHERE movie_id = %s", [movie_id])


def delete_movies_table(cnx: MySQLConnection) -> None:
    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            cursor.execute("DROP TABLE movies")
