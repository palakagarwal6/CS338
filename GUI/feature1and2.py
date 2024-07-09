import streamlit as st  # Streamlit library for GUI
import pandas as pd  # Pandas library for Python data manipulation
import sqlite3  # SQLite library for database operations

# Load CSV data into an SQLite database
def load_data_to_sqlite():
    connection = sqlite3.connect(':memory:')   #  In-memory SQLite database
    # Read CSV files into pandas DataFrames
    movies = pd.read_csv('C:/Education/Uni/4B/CS 338/Project/CS338-main/tables/prod/movie.csv')
    production = pd.read_csv('C:/Education/Uni/4B/CS 338/Project/CS338-main/tables/prod/production.csv')
    classified_in = pd.read_csv('C:/Education/Uni/4B/CS 338/Project/CS338-main/tables/prod/classified_in.csv')
    genres = pd.read_csv('C:/Education/Uni/4B/CS 338/Project/CS338-main/tables/prod/genre.csv')
    comprises_of = pd.read_csv('C:/Education/Uni/4B/CS 338/Project/CS338-main/tables/prod/comprises_of.csv')
    credits = pd.read_csv('C:/Education/Uni/4B/CS 338/Project/CS338-main/tables/prod/credit.csv')
    produced_by = pd.read_csv('C:/Education/Uni/4B/CS 338/Project/CS338-main/tables/prod/produced_by.csv')
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
    sql_query = "SELECT title, overview, vote_average, status, runtime FROM movie WHERE title LIKE ?"  # SQL query to search for movies by title
    return pd.read_sql_query(sql_query, connection, params=[f'%{query}%'])  # Execute and return

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
    """.format(seq=','.join(['?'] * len(genres_list)))  # SQL query to search for top movies by genre
    return pd.read_sql_query(sql_query, connection, params=genres_list + [limit])  # Execute the query and return the results as a DataFrame

# Search movies by production company
def search_movies_by_production(connection, query):
    sql_query = """
        SELECT m.movie_id, m.title, p.production_name
        FROM movie m
        JOIN Produced_By pb ON m.movie_id = pb.movie_id
        JOIN Production p ON pb.production_id = p.production_id
        WHERE p.production_name LIKE ?
        ORDER BY p.production_name, m.movie_id, m.release_date DESC
    """  # SQL query to search for movies by production company
    return pd.read_sql_query(sql_query, connection, params=[f'%{query}%'])  # Execute and return

# Search movies by crew/cast/production member
def search_movies_by_person(connection, query):
    sql_query = """
        SELECT m.title
        FROM movie m
        JOIN Comprises_Of c ON m.movie_id = c.movie_id
        JOIN credit cr ON c.person_id = cr.person_id
        WHERE cr.name LIKE ?
    """  # SQL query to search for movies by person
    return pd.read_sql_query(sql_query, connection, params=[f'%{query}%'])  # Execute and return


# Streamlit app part
def main():
    st.title("Movie Database")  # Title of the Streamlit app

    connection = load_data_to_sqlite()  # Load data and get connection object

    menu = ["Movies", "Crew/Cast/Production", "Production Companies"]
    choice = st.sidebar.selectbox("Menu", menu)    #sidebar

    if choice == "Movies":
        search_type = st.radio("Search by:", ["Title", "Genre"])  # Toggle between searching by title and genre

        if search_type == "Title":
            # Section for searching movies by title
            st.header("Search Movies by Title")  # header
            query = st.text_input("Enter a movie name:")

            if st.button("Search by Title"):  # Button to trigger search
                if query:  # Check if a query is entered
                    results = search_movies_by_title(connection, query)  # Search for movies by title
                    if not results.empty:  # if results are found / not empty
                        for index, result in results.iterrows():  # Iteration over the results
                            st.write(f"**Title:** {result['title']}")
                            st.write(f"**Overview:** {result['overview']}")
                            st.write(f"**Vote Average:** {result['vote_average']}")
                            st.write(f"**Status:** {result['status']}")
                            st.write(f"**Runtime:** {result['runtime']} minutes")
                            st.write("---")  # Separate different movies
                    else:
                        st.write("No results found.")  # Message if no results are found

        # Section for searching top 5/10 movies by genre
        elif search_type == "Genre":
            st.header("Top Movies by Genre")  # Set the header for the genre search section
            genres_list = st.multiselect("Select genres:", ["Action", "Adventure", "Comedy", "Drama", "Fantasy", "Horror", "Romance", "Sci-Fi", "Thriller"])  # Multiselect for selecting genres
            limit = st.radio("Display top results:", [5, 10])  # Radio buttons: top 5/10 results

            if st.button("Search by Genre"):  # Button to search by genre
                if genres_list:  # if genres are selected
                    results = search_movies_by_genre(connection, genres_list, limit)  # Search for top movies by genre
                    if not results.empty:  # Check if results are found
                        for index, result in results.iterrows():  # Iterate over the results
                            st.write(f"**Title:** {result['title']}")
                            st.write(f"**Overview:** {result['overview']}")
                            st.write(f"**Vote Average:** {result['vote_average']}")
                            st.write(f"**Status:** {result['status']}")
                            st.write(f"**Runtime:** {result['runtime']} minutes")
                            st.write("---")  # Separate different movies
                    else:
                        st.write("No results found.")  # Message if no results are found

                        
    # Section for searching movies by crew/cast/production member
    elif choice == "Crew/Cast/Production":
        st.header("Search Movies by Crew/Cast/Production Member")  # header
        query = st.text_input("Enter a crew/cast/production member name:")

        if st.button("Search by Person"):  # Button to trigger search
            if query:  # Check if a query is entered
                results = search_movies_by_person(connection, query)  # Search for movies by person
                if not results.empty:  # if results are found / not empty
                    for index, result in results.iterrows():  # Iteration over the results
                        st.write(f"**Title:** {result['title']}")
                        st.write("---")  # Separate different movies
                else:
                    st.write("No results found.")  # Message if no results are found

                    
    # Section for searching movies by production company
    elif choice == "Production Companies": 
        st.header("Search Movies by Production Company")  # header
        query = st.text_input("Enter a production company name:")
        
        if st.button("Search by Production Company"):  # Button to trigger search
            if query:  # Check if a query is entered
                results = search_movies_by_production(connection, query)  # Search for movies by production company
                if not results.empty:  # if results are found / not empty
                    for index, result in results.iterrows():  # Iteration over the results
                        st.write(f"**Title:** {result['title']}")
                        st.write(f"**Production Company:** {result['production_name']}")
                        st.write("---")  # Separate different movies
                else:
                    st.write("No results found.")  # Message if no results are found

if __name__ == "__main__":
    main()  # Always have this part. Run the main




# To run, go to comman prompt" cd C:\Education\Uni\4B\CS 338\Project\GUI Code, then: streamlit run feature1and2.py
# Can now view Streamlit app in browser.
