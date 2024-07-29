import os
import pandas as pd
import streamlit as st
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

        populate_movies_table(cnx=cnx, csv_file_path=CSV_PATHS["movie"][db_type], update_progress=update_progress, feature="Home")

    df = load_all_movies_from_db(cnx=cnx)
    edited_df = st.data_editor(df)

    if st.button("Save Changes"):
        edited_rows = []
        for index in df.index:
            df_row = df.loc[index]
            edited_df_row = edited_df.loc[index]
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
    selected_genre = st.selectbox("Select a genre", options=list(genre_options.keys()), format_func=lambda x: genre_options[x])

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
