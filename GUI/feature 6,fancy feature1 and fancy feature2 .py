import streamlit as st 
import pandas as pd
from sqlalchemy import create_engine, text
import mysql.connector
from mysql.connector import OperationalError, Error

engine = create_engine('mysql+pymysql://root:123456@localhost:3306/netflix')

st.title('Netflix Movie Explorer')

# Connect to the MySQL database
def connect_to_db():
    return mysql.connector.connect(
        host="localhost", 
        user="root",
        password="123456",
        database="netflix",
        allow_local_infile=True,
    )

# Feature 1: Extended Movie Details
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
        SELECT cr.name AS Name, GROUP_CONCAT(ca.character ORDER BY ca.character SEPARATOR ', ') as Characters, NULL AS Roles  
        FROM credit cr
        JOIN Cast ca ON ca.person_id = cr.person_id
        JOIN Comprises_Of c ON c.person_id = cr.person_id
        JOIN movie m ON c.movie_id = m.movie_id
        WHERE m.movie_id = :movie_id
        GROUP BY cr.name

        UNION

        SELECT cr.name AS Name, NULL AS Characters, GROUP_CONCAT(p.Job_Name SEPARATOR ', ') as Roles
        FROM movie m  
        JOIN comprises_of co ON m.movie_id = co.movie_id
        JOIN credit cr ON co.person_id = cr.person_id
        JOIN performs p ON cr.person_id = p.person_id AND m.movie_id = p.movie_id
        WHERE m.movie_id = :movie_id
        GROUP BY cr.name
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
        db = connect_to_db()  
        cursor = db.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        db.close()  
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