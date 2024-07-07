from db import connect_to_mysql, create_database_if_not_exists, populate_movies_table, create_movies_table, use_database, load_all_movies_from_db, check_movies_table_exists, update_movie_details_in_db, delete_movie_from_db, delete_movies_table
import os

import streamlit as st

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CSV_PATHS = {
    "sample": os.path.join(PROJECT_ROOT, "tables", "sample", "movie.csv"),
    "production": os.path.join(PROJECT_ROOT, "tables", "prod", "movie.csv")
}

# ! Not working
# with st.sidebar:
#     db_type = st.selectbox(label="Select database type",
#                            options=["sample", "production"])

db_type = "sample"

cnx = connect_to_mysql()

create_database_if_not_exists(cnx=cnx, db_name=db_type)
use_database(cnx=cnx, db_name=db_type)

movies_table_exists = check_movies_table_exists(cnx=cnx)

if not movies_table_exists:
    create_movies_table(cnx=cnx)
    with st.spinner("Loading data from CSV into database..."):
        populate_movies_table(
            cnx=cnx, csv_file_path=CSV_PATHS[db_type])

st.title("Movies Database")

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
delete_movie_id = st.selectbox(
    "Select movie ID", movie_ids)

if st.button("Confirm"):
    delete_movie_from_db(cnx=cnx, movie_id=delete_movie_id)
    st.rerun()

if st.button(label="Reset database", type="primary"):
    delete_movies_table(cnx=cnx)
    st.rerun()
