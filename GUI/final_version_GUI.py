import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
import sqlite3
import mysql.connector
from mysql.connector import OperationalError, Error
from db import (
    create_credit_table, create_job_table, populate_job_table, analyze_genre, check_table_exists,
    connect_to_mysql, create_classified_in_table, create_database_if_not_exists, create_genre_tables,
    create_movies_table, create_performs_table, create_produced_by_table, create_production_table,
    create_crew_table, delete_table, get_average_ratings_per_genre, get_crew_statistics,
    populate_credit_table, populate_classified_in_table, populate_genre_table, populate_movies_table,
    populate_performs_table, populate_produced_by_table, populate_production_table, populate_crew_table,
    use_database, load_all_movies_from_db, update_movie_details_in_db, delete_movie_from_db
)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CSV_PATHS = {
    "classified_in": {
        "sample": os.path.join(PROJECT_ROOT, "tables", "sample", "classified_in.csv"),
        "production": os.path.join(PROJECT_ROOT, "tables", "prod", "classified_in.csv")
    },
    "crew": {
        "sample": os.path.join(PROJECT_ROOT, "tables", "sample", "crew.csv"),
        "production": os.path.join(PROJECT_ROOT, "tables", "prod", "crew.csv")
    },
    "movie": {
        "sample": os.path.join(PROJECT_ROOT, "tables", "sample", "movie.csv"),
        "production": os.path.join(PROJECT_ROOT, "tables", "prod", "movie.csv")
    },
    "genre": {
        "sample": os.path.join(PROJECT_ROOT, "tables", "sample", "genre.csv"),
        "production": os.path.join(PROJECT_ROOT, "tables", "prod", "genre.csv")
    },
    "Performs": {
        "sample": os.path.join(PROJECT_ROOT, "tables", "sample", "Performs.csv"),
        "production": os.path.join(PROJECT_ROOT, "tables", "prod", "Performs.csv")
    },
    "Job": {
        "sample": os.path.join(PROJECT_ROOT, "tables", "sample", "Job.csv"),
        "production": os.path.join(PROJECT_ROOT, "tables", "prod", "Job.csv")
    },
    "Credit": {
        "sample": os.path.join(PROJECT_ROOT, "tables", "sample", "credit.csv"),
        "production": os.path.join(PROJECT_ROOT, "tables", "prod", "credit.csv")
    },
    "Produced_By": {
        "sample": os.path.join(PROJECT_ROOT, "tables", "sample", "produced_by.csv"),
        "production": os.path.join(PROJECT_ROOT, "tables", "prod", "produced_by.csv")
    },
    "Production": {
        "sample": os.path.join(PROJECT_ROOT, "tables", "sample", "production.csv"),
        "production": os.path.join(PROJECT_ROOT, "tables", "prod", "production.csv")
    },
}

cnx = connect_to_mysql()

# Set up sidebar options
with st.sidebar:
    db_type = st.selectbox(label="Select database type", options=["sample", "production"])
    mode = st.selectbox(label="Select mode", options=["Home", "Statistics"])

# Database connection and setup
create_database_if_not_exists(cnx=cnx, db_name=db_type)
use_database(cnx=cnx, db_name=db_type)

# Home mode functionality
if mode == "Home":
    st.title("Movies Database")

    movies_table_exists = check_table_exists(cnx, "movies")
    if not movies_table_exists:
        create_movies_table(cnx=cnx, feature="Home")
        progress_bar = st.progress(0, text="Loading movies")


        def update_progress(current, total):
            progress_bar.progress(current / total, text=f"Loading movies ({current}/{total})")


        populate_movies_table(cnx=cnx, csv_file_path=CSV_PATHS["movie"][db_type], update_progress=update_progress,
                              feature="Home")

    df = load_all_movies_from_db(cnx=cnx)
    edited_df = st.data_editor(df)

    if st.button("Save Changes"):
        edited_rows = []
        for index in df.index:
            df_row = df.loc(index)
            edited_df_row = edited_df.loc(index)
            if not df_row.equals(edited_df_row):
                edited_rows.append(edited_df_row)

        for row in edited_rows:
            update_movie_details_in_db(cnx=cnx, row=row)

        st.toast("Changes saved")

    st.header("Delete a movie")
    movie_ids = df["movie_id"].values
    delete_movie_id = st.selectbox("Select movie ID", movie_ids)

    if st.button("Confirm"):
        delete_movie_from_db(cnx=cnx, movie_id=delete_movie_id)
        st.rerun()

    if st.button(label="Reset database", type="primary"):
        delete_table(cnx, "movies")
        st.rerun()

# Statistics mode functionality
elif mode == "Statistics":
    st.title("Statistics")

    if st.button(label="Reset database", type="primary"):
        # Delete tables with foreign keys first
        delete_table(cnx, "Produced_By")
        delete_table(cnx, "Classified_In")
        delete_table(cnx, "Crew")
        delete_table(cnx, "Performs")
        # Delete remaining tables
        delete_table(cnx, "Job")
        delete_table(cnx, "Movie")
        delete_table(cnx, "Genre")
        delete_table(cnx, "Production")
        delete_table(cnx, "Credit")
        st.rerun()

    # Load data into tables if they don't exist
    if not check_table_exists(cnx, "Movie"):
        create_movies_table(cnx)
        progress_bar = st.progress(0, text="Loading movies...")


        def update_progress(current, total):
            progress_bar.progress(current / total, text=f"Loading movies... ({current}/{total})")


        populate_movies_table(cnx, CSV_PATHS["movie"][db_type], update_progress)
    if not check_table_exists(cnx, "Genre"):
        create_genre_tables(cnx)
        populate_genre_table(cnx, CSV_PATHS["genre"][db_type])
    if not check_table_exists(cnx, "Classified_In"):
        create_classified_in_table(cnx)
        populate_classified_in_table(cnx, CSV_PATHS["classified_in"][db_type])
    if not check_table_exists(cnx, "Production"):
        create_production_table(cnx)
        populate_production_table(cnx, CSV_PATHS["Production"][db_type])
    if not check_table_exists(cnx, "Produced_By"):
        create_produced_by_table(cnx)
        populate_produced_by_table(cnx, CSV_PATHS["Produced_By"][db_type])
    if not check_table_exists(cnx, "Job"):
        create_job_table(cnx)
        populate_job_table(cnx, CSV_PATHS["Job"][db_type])
    if not check_table_exists(cnx, "Credit"):
        create_credit_table(cnx)
        populate_credit_table(cnx, CSV_PATHS["Credit"][db_type])
    if not check_table_exists(cnx, "Performs"):
        create_performs_table(cnx)
        populate_performs_table(cnx, CSV_PATHS["Performs"][db_type])
    if not check_table_exists(cnx, "Crew"):
        create_crew_table(cnx)
        populate_crew_table(cnx, CSV_PATHS["crew"][db_type])

    st.header("Best Production Studios by Genre")
    popular_genres_df = get_average_ratings_per_genre(cnx)
    popular_genres_df.index = popular_genres_df.index + 1
    st.table(popular_genres_df)

    genre_options = dict(zip(popular_genres_df['genre_id'], popular_genres_df['name']))
    selected_genre = st.selectbox("Select a genre", options=list(genre_options.keys()),
                                  format_func=lambda x: genre_options[x])

    if st.button("Analyze Genre"):
        genre_analysis_df = analyze_genre(cnx, selected_genre)
        rows_per_page = 10
        total_pages = (len(genre_analysis_df) - 1) // rows_per_page + 1

        current_page = st.number_input('Page number', min_value=1, max_value=total_pages, value=1)
        start_idx = (current_page - 1) * rows_per_page
        end_idx = start_idx + rows_per_page

        st.write(f"Page {current_page} of {total_pages}")
        st.table(genre_analysis_df.iloc[start_idx:end_idx])

    st.header("Crew statistics")
    crew_stats_df = get_crew_statistics(cnx)
    rows_per_page = 10
    total_pages = (len(crew_stats_df) - 1) // rows_per_page + 1

    current_page = st.number_input('Page number', min_value=1, max_value=total_pages, value=1)
    start_idx = (current_page - 1) * rows_per_page
    end_idx = start_idx + rows_per_page

    st.write(f"Page {current_page} of {total_pages}")
    st.dataframe(crew_stats_df.iloc[start_idx:end_idx])

# Feature 1: Extended Movie Details
engine = create_engine('mysql+pymysql://root:Zz13667187517@localhost:3306/netflix')

st.header('Extended Movie Details')

movie_id = st.number_input('Enter Movie ID', min_value=1, step=1)


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


if movie_id:
    df_genres, df_productions, df_cast = get_movie_details(movie_id)

    st.subheader('Movie Genres')
    st.table(df_genres)

    st.subheader('Production Companies')
    st.table(df_productions)

    st.subheader('Cast and Roles')
    st.table(df_cast)

# Feature 2: Movie Genre Statistics
st.header('Movie Genre Statistics')


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


df_movie_count, df_avg_rating = get_genre_statistics()

st.subheader('Genres with the Most Movies')
st.table(df_movie_count)

st.subheader('Genres with the Highest Average Rating')
st.table(df_avg_rating)


# Load CSV data into an SQLite database
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


# Search movies by title
def search_movies_by_title(connection, query):
    sql_query = "SELECT title, overview, vote_average, status, runtime FROM movie WHERE title LIKE ?"
    return pd.read_sql_query(sql_query, connection, params=[f'%{query}%'])


# Search top 5/10 movies by genre
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


# Search movies by production company
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


# Search movies by crew/cast/production member
def search_movies_by_person(connection, query):
    sql_query = """
        SELECT m.title
        FROM movie m 
        JOIN Comprises_Of c ON m.movie_id = c.movie_id
        JOIN credit cr ON c.person_id = cr.person_id
        WHERE cr.name LIKE ?
    """
    return pd.read_sql_query(sql_query, connection, params=[f'%{query}%'])


# Feature 3: Advanced Movie Search
st.header("Advanced Movie Search")

st.write("Use the filters below to search for movies:")

runtime_min = st.text_input("Minimum runtime (in minutes):")
runtime_max = st.text_input("Maximum runtime (in minutes):")
release_year_min = st.text_input("Earliest release year (YYYY):")
release_year_max = st.text_input("Latest release year (YYYY):")
vote_avg_min = st.text_input("Minimum vote average (0-10):")
vote_avg_max = st.text_input("Maximum vote average (0-10):")


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
        cursor = cnx.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        return result
    except Error as e:
        st.error(f"Error: {e}")
        return None


if st.button("Search"):
    results = advanced_search(runtime_min, runtime_max, release_year_min, release_year_max, vote_avg_min, vote_avg_max)
    if results:
        st.write("Search Results:")
        for row in results:
            st.write(row[0])
    else:
        st.write("No movies found matching the criteria.")


# Streamlit app part
def main():
    st.title("Movie Database")

    connection = load_data_to_sqlite()

    menu = ["Movies", "Crew/Cast/Production", "Production Companies"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Movies":
        search_type = st.radio("Search by:", ["Title", "Genre"])

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
            genres_list = st.multiselect("Select genres:",
                                         ["Action", "Adventure", "Comedy", "Drama", "Fantasy", "Horror", "Romance",
                                          "Sci-Fi", "Thriller"])
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

    elif choice == "Crew/Cast/Production":
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

    elif choice == "Production Companies":
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