import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import sqlite3
import mysql.connector
from mysql.connector import OperationalError, Error
import atexit

GLOBAL_CNX = None

def exit_handler():
    if GLOBAL_CNX is not None:
        GLOBAL_CNX.close()

atexit.register(exit_handler)

def connect_to_mysql() -> mysql.connector.MySQLConnection:
    global GLOBAL_CNX

    config = {
        "host": "localhost",
        "user": "root",
        "password": "123456",
        "database": "netflix"
    }

    if GLOBAL_CNX:
        return GLOBAL_CNX
    else:
        GLOBAL_CNX = mysql.connector.connect(**config)
        return GLOBAL_CNX

engine = create_engine('mysql+pymysql://root:123456@localhost:3306/netflix')

def get_movie_details(movie_id):
    with engine.connect() as conn:
        query1 = text(
            "SELECT g.genre_name AS Genre FROM Genre g JOIN Classified_In c ON g.genre_id = c.genre_id JOIN movie m ON c.movie_id = m.movie_id WHERE m.movie_id = :movie_id")
        result1 = conn.execute(query1, {'movie_id': movie_id})
        df_genres = pd.DataFrame(result1.fetchall(), columns=['Genre'])

        query2 = text(
            "SELECT p.production_name AS Productions FROM Production p JOIN Produced_By p1 ON p1.production_id = p.production_id JOIN movie m ON p1.movie_id = m.movie_id WHERE m.movie_id = :movie_id")
        result2 = conn.execute(query2, {'movie_id': movie_id})
        df_productions = pd.DataFrame(result2.fetchall(), columns=['Productions'])

        query3 = text("""
        SELECT cr.name AS Name,  
               GROUP_CONCAT(ca.character ORDER BY ca.character SEPARATOR ', ') as Characters, 
               NULL AS Roles
        FROM credit cr
        JOIN Cast ca ON ca.person_id = cr.person_id 
        JOIN Comprises_Of c ON c.person_id = cr.person_id
        JOIN movie m ON c.movie_id = m.movie_id
        WHERE m.movie_id = :movie_id
        GROUP BY cr.name

        UNION ALL

        SELECT cr.name AS Name,
               NULL AS Characters,
               GROUP_CONCAT(p.Job_Name SEPARATOR ', ') as Roles  
        FROM movie m
        JOIN comprises_of co ON m.movie_id = co.movie_id
        JOIN credit cr ON co.person_id = cr.person_id
        JOIN performs p ON cr.person_id = p.person_id AND m.movie_id = p.movie_id 
        WHERE m.movie_id = :movie_id
        GROUP BY cr.name
        ORDER BY Name
        """)
        result3 = conn.execute(query3, {'movie_id': movie_id})
        df_cast = pd.DataFrame(result3.fetchall(), columns=['Name', 'Characters', 'Roles'])

    return df_genres, df_productions, df_cast

def get_genre_statistics():
    with engine.connect() as conn:
        query1 = text(
            "SELECT g.genre_name, COUNT(*) AS movie_count FROM genre g JOIN Classified_In c ON g.genre_id = c.genre_id GROUP BY g.genre_name ORDER BY movie_count DESC LIMIT 10")
        result1 = conn.execute(query1)
        df_movie_count = pd.DataFrame(result1.fetchall(), columns=['Genre', 'Movie Count'])

        query2 = text(
            "SELECT g.genre_name, ROUND(AVG(m.vote_average), 2) AS avg_rating FROM genre g JOIN Classified_In c ON g.genre_id = c.genre_id JOIN movie m ON c.movie_id = m.movie_id GROUP BY g.genre_name ORDER BY avg_rating DESC LIMIT 10")
        result2 = conn.execute(query2)
        df_avg_rating = pd.DataFrame(result2.fetchall(), columns=['Genre', 'Avg. Rating'])

    return df_movie_count, df_avg_rating

def advanced_search(runtime_min, runtime_max, release_year_min, release_year_max, vote_avg_min, vote_avg_max):
    query = "SELECT title FROM movie WHERE 1=1"
    params = []

    if runtime_min:
        query += " AND runtime >= %s"
        params.append(runtime_min)
    if runtime_max:
        query += " AND runtime <= %s"
        params.append(runtime_max)

    if release_year_min:
        query += " AND YEAR(release_date) >= %s"
        params.append(release_year_min)
    if release_year_max:
        query += " AND YEAR(release_date) <= %s"
        params.append(release_year_max)

    if vote_avg_min:
        query += " AND vote_average >= %s"
        params.append(vote_avg_min)
    if vote_avg_max:
        query += " AND vote_average <= %s"
        params.append(vote_avg_max)

    query += " LIMIT 30"

    try:
        cnx = connect_to_mysql()
        cursor = cnx.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        return result
    except Error as e:
        st.error(f"Error: {e}")
        return None

def load_data_to_sqlite():
    connection = sqlite3.connect(':memory:')
    # Read CSV files into pandas DataFrames
    movies = pd.read_csv('../tables/prod/movie.csv')
    production = pd.read_csv('../tables/prod/production.csv')
    classified_in = pd.read_csv('../tables/prod/classified_in.csv')
    genres = pd.read_csv('../tables/prod/genre.csv')
    comprises_of = pd.read_csv('../tables/prod/comprises_of.csv')
    credits = pd.read_csv('../tables/prod/credit.csv')
    produced_by = pd.read_csv('../tables/prod/produced_by.csv')
    # Store DataFrames into SQLite tables
    movies.to_sql('movie', connection, index=False, if_exists='replace')
    classified_in.to_sql('Classified_In', connection, index=False, if_exists='replace')
    genres.to_sql('genre', connection, index=False, if_exists='replace')
    comprises_of.to_sql('Comprises_Of', connection, index=False, if_exists='replace')
    credits.to_sql('credit', connection, index=False, if_exists='replace')
    produced_by.to_sql('Produced_By', connection, index=False, if_exists='replace')
    production.to_sql('Production', connection, index=False, if_exists='replace')
    return connection

def search_movies_by_title(connection, query):
    sql_query = "SELECT title, overview, vote_average, status, runtime FROM movie WHERE title LIKE ?"
    return pd.read_sql_query(sql_query, connection, params=[f'%{query}%'])

def search_movies_by_genre(connection, genres_list, limit):
    sql_query = """
        SELECT m.title, m.overview, m.vote_average, m.status, m.runtime
        FROM movie m
        JOIN Classified_In c ON m.movie_id = c.movie_id
        JOIN genre g ON c.genre_id = g.genre_id
        WHERE g.genre_name IN ({seq})  
        ORDER BY m.vote_average DESC
        LIMIT ?
    """.format(seq=','.join(['?'] * len(genres_list)))
    return pd.read_sql_query(sql_query, connection, params=genres_list + [limit])

def search_movies_by_production(connection, query):
    sql_query = """
        SELECT m.movie_id, m.title, p.production_name 
        FROM movie m
        JOIN Produced_By pb ON m.movie_id = pb.movie_id
        JOIN Production p ON pb.production_id = p.production_id
        WHERE p.production_name LIKE ?
        ORDER BY p.production_name, m.movie_id, m.release_date DESC
    """
    return pd.read_sql_query(sql_query, connection, params=[f'%{query}%'])

def search_movies_by_person(connection, query):
    sql_query = """
        SELECT m.title
        FROM movie m 
        JOIN Comprises_Of c ON m.movie_id = c.movie_id
        JOIN credit cr ON c.person_id = cr.person_id
        WHERE cr.name LIKE ?
    """
    return pd.read_sql_query(sql_query, connection, params=[f'%{query}%'])

def main():
    st.title("Netflix Movie Explorer")

    menu = ["Extended Movie Details", "Movie Genre Statistics", "Advanced Movie Search", "Sidebar Search"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Extended Movie Details":
        st.header('Extended Movie Details')
        movie_id = st.number_input('Enter Movie ID', min_value=1, step=1)
        if movie_id:
            df_genres, df_productions, df_cast = get_movie_details(movie_id)
            st.subheader('Movie Genres')
            st.table(df_genres)
            st.subheader('Production Companies')
            st.table(df_productions)
            st.subheader('Cast and Roles')
            st.table(df_cast)

    elif choice == "Movie Genre Statistics":
        st.header('Movie Genre Statistics')
        df_movie_count, df_avg_rating = get_genre_statistics()
        st.subheader('Genres with the Most Movies')
        st.table(df_movie_count)
        st.subheader('Genres with the Highest Average Rating')
        st.table(df_avg_rating)

    elif choice == "Advanced Movie Search":
        st.header("Advanced Movie Search")
        st.write("Use the filters below to search for movies:")
        runtime_min = st.text_input("Minimum runtime (in minutes):")
        runtime_max = st.text_input("Maximum runtime (in minutes):")
        release_year_min = st.text_input("Earliest release year (YYYY):")
        release_year_max = st.text_input("Latest release year (YYYY):")
        vote_avg_min = st.text_input("Minimum vote average (0-10):")
        vote_avg_max = st.text_input("Maximum vote average (0-10):")
        if st.button("Search"):
            results = advanced_search(runtime_min, runtime_max, release_year_min, release_year_max, vote_avg_min, vote_avg_max)
            if results:
                st.write("Search Results:")
                for row in results:
                    st.write(row[0])
            else:
                st.write("No movies found matching the criteria.")

    elif choice == "Sidebar Search":
        connection = load_data_to_sqlite()
        search_type = st.radio("Search by:", ["Title", "Genre", "Crew/Cast/Production", "Production Companies"])

        if search_type == "Title":
            st.header("Search Movies by Title")
            query = st.text_input("Enter a movie name:")
            if st.button("Search by Title"):
                if query:
                    results = search_movies_by_title(connection, query)
                    if not results.empty:
                        for index, result in results.iterrows():
                            st.write(f"**Title:** {result['title']}")
                            st.write(f"**Overview:** {result['overview']}")
                            st.write(f"**Vote Average:** {result['vote_average']}")
                            st.write(f"**Status:** {result['status']}")
                            st.write(f"**Runtime:** {result['runtime']} minutes")
                            st.write("---")
                    else:
                        st.write("No results found.")

        elif search_type == "Genre":
            st.header("Top Movies by Genre")
            genres_list = st.multiselect("Select genres:", ["Action", "Adventure", "Comedy", "Drama", "Fantasy", "Horror", "Romance", "Sci-Fi", "Thriller"])
            limit = st.radio("Display top results:", [5, 10])
            if st.button("Search by Genre"):
                if genres_list:
                    results = search_movies_by_genre(connection, genres_list, limit)
                    if not results.empty:
                        for index, result in results.iterrows():
                            st.write(f"**Title:** {result['title']}")
                            st.write(f"**Overview:** {result['overview']}")
                            st.write(f"**Vote Average:** {result['vote_average']}")
                            st.write(f"**Status:** {result['status']}")
                            st.write(f"**Runtime:** {result['runtime']} minutes")
                            st.write("---")
                    else:
                        st.write("No results found.")

        elif search_type == "Crew/Cast/Production":
            st.header("Search Movies by Crew/Cast/Production Member")
            query = st.text_input("Enter a crew/cast/production member name:")
            if st.button("Search by Person"):
                if query:
                    results = search_movies_by_person(connection, query)
                    if not results.empty:
                        for index, result in results.iterrows():
                            st.write(f"**Title:** {result['title']}")
                            st.write("---")
                    else:
                        st.write("No results found.")

        elif search_type == "Production Companies":
            st.header("Search Movies by Production Company")
            query = st.text_input("Enter a production company name:")
            if st.button("Search by Production Company"):
                if query:
                    results = search_movies_by_production(connection, query)
                    if not results.empty:
                        for index, result in results.iterrows():
                            st.write(f"**Title:** {result['title']}")
                            st.write(f"**Production Company:** {result['production_name']}")
                            st.write("---")
                    else:
                        st.write("No results found.")

if __name__ == "__main__":
    main()