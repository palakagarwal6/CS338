import pandas as pd
import mysql.connector
from mysql.connector import MySQLConnection
import atexit

GLOBAL_CNX = None


def exit_handler():
    if GLOBAL_CNX is not None:
        GLOBAL_CNX.close()


atexit.register(exit_handler)


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
            CREATE TABLE IF NOT EXISTS Movie(
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


def populate_movies_table(cnx: MySQLConnection, csv_file_path: str) -> None:
    df = pd.read_csv(csv_file_path)
    df = df.drop_duplicates(subset='movie_id', keep='first')

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
        INSERT INTO Movie(movie_id, title, overview, status, release_date, adult, video, runtime, vote_average, vote_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = tuple(row)

        if cnx and cnx.is_connected():
            with cnx.cursor() as cursor:
                cursor.execute(query, values)


def load_all_movies_from_db(cnx: MySQLConnection) -> pd.DataFrame:
    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            query = "SELECT * FROM Movie"
            df = pd.read_sql(query, cnx)
            return df


def update_movie_details_in_db(cnx: MySQLConnection, row: pd.Series) -> None:
    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            query = """
            UPDATE Movie
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
            cursor.eXxecute(
                "DELETE FROM Movie WHERE movie_id = %s", [movie_id])


def delete_table(cnx: MySQLConnection, table_name: str) -> None:
    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")


def create_crew_table(cnx: MySQLConnection) -> None:
    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            query = """
            CREATE TABLE IF NOT EXISTS crew (
                crew_id INT PRIMARY KEY,
                name VARCHAR(255),
                job VARCHAR(255),
                rating FLOAT
            )
            """
            cursor.execute(query)


def populate_crew_table(cnx: MySQLConnection, csv_file_path: str) -> None:
    df = pd.read_csv(csv_file_path)

    df = df.astype({
        'crew_id': int,
        'name': str,
        'job': str,
        'rating': float
    })

    for _, row in df.iterrows():
        query = """
        INSERT INTO crew (crew_id, name, job, rating)
        VALUES (%s, %s, %s, %s)
        """
        values = tuple(row)

        if cnx and cnx.is_connected():
            with cnx.cursor() as cursor:
                cursor.execute(query, values)


def get_crew_statistics(cnx: MySQLConnection) -> pd.DataFrame:
    if cnx and cnx.is_connected():
        query = """
        SELECT cr.name, c.person_id, j.job_name, COUNT(m.movie_id) AS num_movies, AVG(m.vote_average) AS avg_rating
        FROM Movie m
        JOIN Classified_In ci ON m.movie_id = ci.movie_id
        JOIN Genre g ON ci.genre_id = g.genre_id
        JOIN Performs p ON p.movie_id = m.movie_id
        JOIN Crew c ON p.person_id = c.person_id
        JOIN Job j ON p.job_name = j.job_name
        JOIN Credit cr ON c.person_id = cr.person_id
        GROUP BY cr.name, c.person_id, j.job_name
        ORDER BY avg_rating DESC
        """
        df = pd.read_sql(query, cnx)
        return df


def create_genre_tables(cnx: MySQLConnection) -> None:
    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Genre (
                genre_id INT PRIMARY KEY,
                name VARCHAR(255)
            )
            """)


def populate_genre_table(cnx: MySQLConnection, csv_file_path: str) -> None:
    if cnx and cnx.is_connected():
        data = pd.read_csv(csv_file_path)
        data = data.drop_duplicates(subset="genre_id", keep="first")

        with cnx.cursor() as cursor:
            for _, row in data.iterrows():
                query = f"INSERT INTO Genre (genre_id, name) VALUES (%s, %s)"
                cursor.execute(query, tuple(row))

        cnx.commit()


def populate_classified_in_table(cnx: MySQLConnection, csv_file_path: str) -> None:
    if cnx and cnx.is_connected():
        data = pd.read_csv(csv_file_path)
        # data = data.drop_duplicates(
        #     subset=["movie_id", "genre_id"], keep="first")

        with cnx.cursor() as cursor:
            for _, row in data.iterrows():
                query = f"INSERT INTO Classified_In (movie_id, genre_id) VALUES (%s, %s)"
                cursor.execute(query, tuple(row))

        cnx.commit()


def get_popular_genres(cnx: MySQLConnection) -> pd.DataFrame:
    if cnx and cnx.is_connected():
        query = """
        SELECT g.name, COUNT(ci.movie_id) AS num_movies
        FROM Genre g
        JOIN Classified_In ci ON g.genre_id = ci.genre_id
        GROUP BY g.name
        ORDER BY num_movies DESC
        """
        df = pd.read_sql(query, cnx)
        return df


def get_average_ratings_per_genre(cnx: MySQLConnection) -> pd.DataFrame:
    if cnx and cnx.is_connected():
        query = """
        SELECT g.name, g.genre_id, AVG(m.vote_average) AS avg_rating
        FROM Genre g
        JOIN Classified_In ci ON g.genre_id = ci.genre_id
        JOIN Movie m ON ci.movie_id = m.movie_id
        GROUP BY g.name, g.genre_id
        ORDER BY avg_rating DESC
        """
        df = pd.read_sql(query, cnx)
        return df


def analyze_genre(cnx: MySQLConnection, genre_id: int) -> pd.DataFrame:
    if cnx and cnx.is_connected():
        query = """
        SELECT p.production_name, AVG(m.vote_average) AS vote_score  
        FROM Movie m 
        JOIN Classified_In ci ON m.movie_id = ci.movie_id 
        JOIN Genre g ON ci.genre_id = g.genre_id 
        JOIN Produced_By pb ON m.movie_id = pb.movie_id 
        JOIN Production p ON pb.production_id = p.production_id 
        WHERE g.genre_id = %s
        GROUP BY p.production_name ORDER BY vote_score DESC;
        """
        df = pd.read_sql(query, cnx, params=[genre_id])
        return df


def check_table_exists(cnx: MySQLConnection, table_name: str) -> bool:
    with cnx.cursor() as cursor:
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        result = cursor.fetchone()
        table_exists = result is not None
        return table_exists


"""
Classified_In table
"""


def create_classified_in_table(cnx: MySQLConnection) -> None:
    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            query = """
            CREATE TABLE IF NOT EXISTS Classified_In (
                movie_id INT,
                genre_id INT,
                PRIMARY KEY (movie_id, genre_id),
                FOREIGN KEY (movie_id) REFERENCES Movie(movie_id),
                FOREIGN KEY (genre_id) REFERENCES Genre(genre_id)
            );
            """
            cursor.execute(query)


def populate_classified_in_table(cnx: MySQLConnection, csv_file_path: str) -> None:
    if cnx and cnx.is_connected():
        data = pd.read_csv(csv_file_path)

        with cnx.cursor() as cursor:
            for _, row in data.iterrows():
                query = f"INSERT INTO Classified_In (movie_id, genre_id) VALUES (%s, %s)"
                cursor.execute(query, tuple(row))

        cnx.commit()


"""
Production table
"""


def create_production_table(cnx: MySQLConnection) -> None:
    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            query = """
            CREATE TABLE IF NOT EXISTS Production (
                production_id INT,
                production_name VARCHAR(255),
                PRIMARY KEY (production_id)
            );
            """
            cursor.execute(query)


def populate_production_table(cnx: MySQLConnection, csv_file_path: str) -> None:
    if cnx and cnx.is_connected():
        data = pd.read_csv(csv_file_path)

        with cnx.cursor() as cursor:
            for _, row in data.iterrows():
                query = f"INSERT INTO Production VALUES (%s, %s)"
                cursor.execute(query, tuple(row))

        cnx.commit()


"""
Produced by table
"""


def create_produced_by_table(cnx: MySQLConnection) -> None:
    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            query = """
            CREATE TABLE IF NOT EXISTS Produced_By (
                movie_id INT,
                production_id INT,
                PRIMARY KEY (movie_id, production_id),
                FOREIGN KEY (movie_id) REFERENCES Movie(movie_id),
                FOREIGN KEY (production_id) REFERENCES Production(production_id)
            );
            """
            cursor.execute(query)


def populate_produced_by_table(cnx: MySQLConnection, csv_file_path: str) -> None:
    if cnx and cnx.is_connected():
        data = pd.read_csv(csv_file_path)

        with cnx.cursor() as cursor:
            for _, row in data.iterrows():
                query = f"INSERT INTO Produced_By VALUES (%s, %s)"
                cursor.execute(query, tuple(row))

        cnx.commit()
