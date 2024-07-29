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
        "password": "Zz13667187517"
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


def create_movies_table(cnx: MySQLConnection, feature: str = "Statistics") -> bool:
    if feature == "Statistics":
        name = "Movie"
    else:
        name = "movies"
    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            query = f"""
            CREATE TABLE IF NOT EXISTS {name}(
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

def populate_movies_table(cnx: MySQLConnection, csv_file_path: str, update_progress, feature: str = "Statistics") -> None:
    if feature == "Statistics":
        name = "Movie"
    else:
        name = "movies"

    df = pd.read_csv(csv_file_path, na_values='nan')
    df = df.drop_duplicates(subset='movie_id', keep='first')

    df['movie_id'] = pd.to_numeric(df['movie_id'], errors='coerce')
    df['adult'] = df['adult'].astype(bool, errors='ignore')
    df['runtime'] = pd.to_numeric(df['runtime'], errors='coerce')
    df['vote_average'] = pd.to_numeric(df['vote_average'], errors='coerce')
    df['vote_count'] = pd.to_numeric(df['vote_count'], errors='coerce')

    df.dropna(subset=['movie_id', 'runtime',
              'vote_average', 'vote_count'], inplace=True)

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

    total_rows = len(df)
    for i, (_, row) in enumerate(df.iterrows()):
        query = f"""
        INSERT IGNORE INTO {name}(movie_id, title, overview, status, release_date, adult, video, runtime, vote_average, vote_count)
        VALUES (
            NULLIF(%s, 'nan'),
            NULLIF(%s, 'nan'),
            NULLIF(%s, 'nan'),
            NULLIF(%s, 'nan'),
            NULLIF(%s, 'nan'),
            NULLIF('%s', 'nan'),
            NULLIF('%s', 'nan'),
            NULLIF(%s, 'nan'),
            NULLIF(%s, 'nan'),
            NULLIF(%s, 'nan')
        )
        """

        values = list(row)
        for vi in range(len(values)):
            v = values[vi]
            if pd.isnull(v):
                values[vi] = 'nan'
            if vi > 1 and vi < 4:
                values[vi] = v.replace("'", "''")

        if cnx and cnx.is_connected():
            with cnx.cursor() as cursor:
                cursor.execute(query, values)

        update_progress(i + 1, total_rows)
# def populate_movies_table(cnx: MySQLConnection, csv_file_path: str, update_progress, feature: str = "Statistics") -> None:
#     if feature == "Statistics":
#         name = "Movie"
#     else:
#         name = "movies"
#
#     df = pd.read_csv(csv_file_path)
#     df = df.drop_duplicates(subset='movie_id', keep='first')
#
#     df['movie_id'] = pd.to_numeric(df['movie_id'], errors='coerce')
#     df['adult'] = df['adult'].astype(bool, errors='ignore')
#     df['runtime'] = pd.to_numeric(df['runtime'], errors='coerce')
#     df['vote_average'] = pd.to_numeric(df['vote_average'], errors='coerce')
#     df['vote_count'] = pd.to_numeric(df['vote_count'], errors='coerce')
#
#     df.dropna(subset=['movie_id', 'runtime',
#               'vote_average', 'vote_count'], inplace=True)
#
#     df = df.astype({
#         'movie_id': int,
#         'title': str,
#         'overview': str,
#         'status': str,
#         'adult': bool,
#         'runtime': int,
#         'vote_average': float,
#         'vote_count': int
#     })
#
#     total_rows = len(df)
#     for i, (_, row) in enumerate(df.iterrows()):
#         query = f"""
#         INSERT IGNORE INTO {name}(movie_id, title, overview, status, release_date, adult, video, runtime, vote_average, vote_count)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """
#
#         values = list(row)
#
#         if cnx and cnx.is_connected():
#             with cnx.cursor() as cursor:
#                 cursor.execute(query, values)
#
#         update_progress(i + 1, total_rows)


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


def delete_table(cnx: MySQLConnection, table_name: str) -> None:
    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")


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
        LIMIT 100
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
        data = pd.read_csv(csv_file_path, na_values='nan')
        data = data.drop_duplicates(subset="genre_id", keep="first")

        with cnx.cursor() as cursor:
            for _, row in data.iterrows():
                values = list(row)
                for vi in range(len(values)):
                    v = values[vi]
                    if pd.isnull(v):
                        values[vi] = 'nan'
                    if isinstance(v, str):
                        values[vi] = v.replace("'", "''")
                query = f"INSERT IGNORE INTO Genre (genre_id, name) VALUES (NULLIF(%s, 'nan'), NULLIF(%s, 'nan'))"
                cursor.execute(query, values)

        cnx.commit()
# def populate_genre_table(cnx: MySQLConnection, csv_file_path: str) -> None:
#     if cnx and cnx.is_connected():
#         data = pd.read_csv(csv_file_path)
#         data = data.drop_duplicates(subset="genre_id", keep="first")
#
#         with cnx.cursor() as cursor:
#             for _, row in data.iterrows():
#                 query = f"INSERT IGNORE INTO Genre (genre_id, name) VALUES (%s, %s)"
#                 cursor.execute(query, tuple(row))
#
#         cnx.commit()


def populate_classified_in_table(cnx: MySQLConnection, csv_file_path: str) -> None:
    if cnx and cnx.is_connected():
        data = pd.read_csv(csv_file_path)
        # data = data.drop_duplicates(
        #     subset=["movie_id", "genre_id"], keep="first")

        with cnx.cursor() as cursor:
            for _, row in data.iterrows():
                values = list(row)
                for vi in range(len(values)):
                    v = values[vi]
                    if pd.isnull(v):
                        values[vi] = 'nan'
                    if isinstance(v, str):
                        values[vi] = v.replace("'", "''")
                query = f"INSERT IGNORE INTO Classified_In (movie_id, genre_id) VALUES (%s, %s)"
                cursor.execute(query, values)

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
                FOREIGN KEY (movie_id) REFERENCES Movie(movie_id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (genre_id) REFERENCES Genre(genre_id) 
            );
            """
            cursor.execute(query)


def populate_classified_in_table(cnx: MySQLConnection, csv_file_path: str) -> None:
    if cnx and cnx.is_connected():
        data = pd.read_csv(csv_file_path)

        with cnx.cursor() as cursor:
            for _, row in data.iterrows():
                values = list(row)
                for vi in range(len(values)):
                    v = values[vi]
                    if pd.isnull(v):
                        values[vi] = 'nan'
                    if isinstance(v, str):
                        values[vi] = v.replace("'", "''")
                query = f"INSERT IGNORE INTO Classified_In (movie_id, genre_id) VALUES (%s, %s)"
                cursor.execute(query, values)

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
                values = list(row)
                for vi in range(len(values)):
                    v = values[vi]
                    if pd.isnull(v):
                        values[vi] = 'nan'
                    if isinstance(v, str):
                        values[vi] = v.replace("'", "''")
                query = f"INSERT IGNORE INTO Production VALUES (%s, %s)"
                cursor.execute(query, values)

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
                FOREIGN KEY (movie_id) REFERENCES Movie(movie_id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (production_id) REFERENCES Production(production_id)
            );
            """
            cursor.execute(query)


def populate_produced_by_table(cnx: MySQLConnection, csv_file_path: str) -> None:
    if cnx and cnx.is_connected():
        data = pd.read_csv(csv_file_path)

        with cnx.cursor() as cursor:
            for _, row in data.iterrows():
                values = list(row)
                for vi in range(len(values)):
                    v = values[vi]
                    if pd.isnull(v):
                        values[vi] = 'nan'
                    if isinstance(v, str):
                        values[vi] = v.replace("'", "''")
                query = f"INSERT IGNORE INTO Produced_By VALUES (%s, %s)"
                cursor.execute(query, values)

        cnx.commit()


"""
Crew table
"""


def create_crew_table(cnx: MySQLConnection) -> None:
    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            query = """
            CREATE TABLE IF NOT EXISTS Crew (
                person_id INT PRIMARY KEY,
                FOREIGN KEY (person_id) REFERENCES Credit(person_id)
            );
            """
            cursor.execute(query)


def populate_crew_table(cnx: MySQLConnection, csv_file_path: str) -> None:
    if cnx and cnx.is_connected():
        data = pd.read_csv(csv_file_path)

        with cnx.cursor() as cursor:
            for _, row in data.iterrows():
                values = list(row)
                for vi in range(len(values)):
                    v = values[vi]
                    if pd.isnull(v):
                        values[vi] = 'nan'
                    if isinstance(v, str):
                        values[vi] = v.replace("'", "''")
                try:
                    query = f"INSERT IGNORE INTO Crew VALUES (%s)"
                    cursor.execute(query, values)
                except Exception as e:
                    print("Error processing", row)
                    print(e)

        cnx.commit()


"""
Performs table
"""


def create_performs_table(cnx: MySQLConnection) -> None:
    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            query = """
            CREATE TABLE IF NOT EXISTS Performs (
                job_name VARCHAR(255),
                person_id INT,
                movie_id INT,
                PRIMARY KEY (person_id, movie_id),
                FOREIGN KEY (person_id) REFERENCES Credit(person_id),
                FOREIGN KEY (movie_id) REFERENCES Movie(movie_id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (job_name) REFERENCES Job(job_name)
            );
            """
            cursor.execute(query)

def populate_performs_table(cnx: MySQLConnection, csv_file_path: str) -> None:
    if cnx and cnx.is_connected():
        data = pd.read_csv(csv_file_path, na_values='nan')

        with cnx.cursor() as cursor:
            for _, row in data.iterrows():
                values = list(row)
                for vi in range(len(values)):
                    v = values[vi]
                    if pd.isnull(v):
                        values[vi] = 'nan'
                    if isinstance(v, str):
                        values[vi] = v.replace("'", "''")
                query = f"INSERT IGNORE INTO Performs VALUES (NULLIF(%s, 'nan'), NULLIF(%s, 'nan'), NULLIF(%s, 'nan'))"
                cursor.execute(query, values)

        cnx.commit()
# def populate_performs_table(cnx: MySQLConnection, csv_file_path: str) -> None:
#     if cnx and cnx.is_connected():
#         data = pd.read_csv(csv_file_path)
#
#         with cnx.cursor() as cursor:
#             for _, row in data.iterrows():
#                 query = f"INSERT IGNORE INTO Performs VALUES (%s, %s, %s)"
#                 cursor.execute(query, tuple(row))
#
#         cnx.commit()


"""
Job table
"""


def create_job_table(cnx: MySQLConnection) -> None:
    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            query = """
            CREATE TABLE IF NOT EXISTS Job (
                job_name VARCHAR(255) PRIMARY KEY
            );
            """
            cursor.execute(query)


def populate_job_table(cnx: MySQLConnection, csv_file_path: str) -> None:
    if cnx and cnx.is_connected():
        data = pd.read_csv(csv_file_path)

        with cnx.cursor() as cursor:
            for _, row in data.iterrows():
                values = list(row)
                for vi in range(len(values)):
                    v = values[vi]
                    if pd.isnull(v):
                        values[vi] = 'nan'
                    if isinstance(v, str):
                        values[vi] = v.replace("'", "''")
                query = f"INSERT IGNORE INTO Job VALUES (%s)"
                cursor.execute(query, values)

        cnx.commit()


"""
Credit table
"""


def create_credit_table(cnx: MySQLConnection) -> None:
    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            query = """
            CREATE TABLE IF NOT EXISTS Credit (
                person_id INT PRIMARY KEY,
                name VARCHAR(255)
            );
            """
            cursor.execute(query)

def populate_credit_table(cnx: MySQLConnection, csv_file_path: str) -> None:
    if cnx and cnx.is_connected():
        data = pd.read_csv(csv_file_path, na_values='nan')
        data = data.drop_duplicates(subset="person_id", keep="first")

        with cnx.cursor() as cursor:
            for _, row in data.iterrows():
                values = list(row)
                for vi in range(len(values)):
                    v = values[vi]
                    if pd.isnull(v):
                        values[vi] = 'nan'
                    if isinstance(v, str):
                        values[vi] = v.replace("'", "''")
                query = f"INSERT IGNORE INTO Credit VALUES (NULLIF(%s, 'nan'), NULLIF(%s, 'nan'))"
                cursor.execute(query, values)

        cnx.commit()
# def populate_credit_table(cnx: MySQLConnection, csv_file_path: str) -> None:
#     if cnx and cnx.is_connected():
#         data = pd.read_csv(csv_file_path)
#         data = data.drop_duplicates(subset="person_id", keep="first")
#
#         with cnx.cursor() as cursor:
#             for _, row in data.iterrows():
#                 query = f"INSERT IGNORE INTO Credit VALUES (%s, %s)"
#                 cursor.execute(query, tuple(row))
#
#         cnx.commit()