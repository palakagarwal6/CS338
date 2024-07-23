from db import populate_genre_table, delete_table, populate_movies_table, create_movies_table, create_classified_in_table, check_table_exists, create_genre_tables, populate_classified_in_table, get_popular_genres, get_average_ratings_per_genre, analyze_genre, use_database, connect_to_mysql, create_database_if_not_exists
import os

import streamlit as st

PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..'))
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
    "credit": {
        "sample": os.path.join(PROJECT_ROOT, "tables", "sample", "credit.csv"),
        "production": os.path.join(PROJECT_ROOT, "tables", "prod", "credit.csv")
    },
    "Produced_by": {
        "sample": os.path.join(PROJECT_ROOT, "tables", "sample", "produced_by.csv"),
        "production": os.path.join(PROJECT_ROOT, "tables", "prod", "produced_by.csv")
    },
    "Production": {
        "sample": os.path.join(PROJECT_ROOT, "tables", "sample", "production.csv"),
        "production": os.path.join(PROJECT_ROOT, "tables", "prod", "production.csv")
    },
}

db_type = "sample"

cnx = connect_to_mysql()
create_database_if_not_exists(cnx=cnx, db_name=db_type)
use_database(cnx=cnx, db_name=db_type)

st.title("Statistics")


cnx = connect_to_mysql()
if not check_table_exists(cnx, "Movie"):
    create_movies_table(cnx)
    populate_movies_table(cnx, CSV_PATHS["movie"][db_type])
if not check_table_exists(cnx, "Genre"):
    create_genre_tables(cnx)
    populate_genre_table(cnx, CSV_PATHS["genre"][db_type])
if not check_table_exists(cnx, "Classified_In"):
    create_classified_in_table(cnx)
    populate_classified_in_table(cnx, CSV_PATHS["classified_in"][db_type])

# st.header("Upload CSV to Populate Genre Tables")
# csv_file_path = st.file_uploader("Choose a CSV file", type="csv")

# if csv_file_path is not None:
#     populate_genre_tables(cnx, csv_file_path)
#     st.success("Tables populated successfully")

st.header("Popular Genres")

popular_genres_df = get_average_ratings_per_genre(cnx)
# So that the first column in the table starts from 1 and not 0
popular_genres_df.index = popular_genres_df.index + 1

st.table(popular_genres_df)

genre_options = dict(
    zip(popular_genres_df['genre_id'], popular_genres_df['name']))
selected_genre = st.selectbox("Select a genre", options=list(
    genre_options.keys()), format_func=lambda x: genre_options[x])

if st.button("Analyze Genre"):
    genre_analysis_df = analyze_genre(cnx, selected_genre)
    st.table(genre_analysis_df)


if st.button(label="Reset database", type="primary"):
    delete_table(cnx, "Classified_In")
    delete_table(cnx, "Movie")
    delete_table(cnx, "Genre")
    st.rerun()
