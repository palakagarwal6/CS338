import streamlit as st
import pandas as pd
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy_utils import database_exists, create_database

def create_engine_and_connect(db_name: str):
    """
    Create a SQLAlchemy engine and connect to the specified MySQL database.
    Create the database if it doesn't exist.

    Args:
        db_name (str): The name of the database to connect to.

    Returns:
        sqlalchemy.engine.base.Engine: The SQLAlchemy engine object.
    """
    try:
        # Base connection URL for MySQL
        base_url = f"mysql+mysqlconnector://root:password@localhost/"
        # Full database URL
        db_url = f"{base_url}{db_name}"

        # Create an engine for the base URL to check/create the database
        base_engine = create_engine(base_url)
    
        # Check if the database exists, and create it if it doesn't
        if not database_exists(db_url):
            create_database(db_url)
            st.success(f"Database '{db_name}' created successfully.")

        # Create an engine for the database URL
        engine = create_engine(db_url)
        return engine
    except SQLAlchemyError as e:
        st.error(f"Error: {e}")
        return None

def determine_column_types(df: pd.DataFrame) -> dict:
    """
    Determine MySQL column types based on the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to analyze.

    Returns:
        dict: A dictionary where keys are column names and values are MySQL column types.
    """
    column_types = {}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            if pd.api.types.is_integer_dtype(df[col]):
                column_types[col] = "INT"
            else:
                column_types[col] = "FLOAT"
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            column_types[col] = "DATETIME"
        else:
            column_types[col] = "TEXT"
    return column_types

def load_csv_to_mysql(file_path: str, table_name: str, db_name: str) -> None:
    """
    Load a CSV file into a MySQL database table.

    Args:
        file_path (str): The path to the CSV file.
        table_name (str): The name of the table to create and insert data into.
        db_name (str): The name of the database to connect to.
    """
    engine = create_engine_and_connect(db_name)
    if engine is None:
        return
    
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)
    
    # Determine column types
    column_types = determine_column_types(df)
    
    # Create table if it doesn't exist and add a primary key column
    with engine.connect() as conn:
        conn.execute(text(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            {', '.join([f'{col} {col_type}' for col, col_type in column_types.items()])}
        )
        """))
    
        # Insert data into the table
        df.to_sql(table_name, conn, if_exists='append', index=False)

def display_data(table_name: str, db_name: str, limit: int, offset: int) -> pd.DataFrame:
    """
    Display paginated data from a MySQL database table.

    Args:
        table_name (str): The name of the table to query data from.
        db_name (str): The name of the database to connect to.
        limit (int): The number of rows to fetch.
        offset (int): The offset from where to start fetching rows.

    Returns:
        pd.DataFrame: The queried data as a DataFrame.
    """
    engine = create_engine_and_connect(db_name)
    if engine is None:
        return pd.DataFrame()
    
    query = f"SELECT * FROM {table_name} LIMIT %s OFFSET %s"
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params=(limit, offset))
    return df

def get_total_rows(table_name: str, db_name: str) -> int:
    """
    Get the total number of rows in a MySQL database table.

    Args:
        table_name (str): The name of the table to query data from.
        db_name (str): The name of the database to connect to.

    Returns:
        int: The total number of rows in the table.
    """
    engine = create_engine_and_connect(db_name)
    if engine is None:
        return 0
    
    query = f"SELECT COUNT(*) FROM {table_name}"
    with engine.connect() as conn:
        result = conn.execute(text(query))
        total_rows = result.scalar()
    return total_rows

def delete_row_from_table(table_name: str, db_name: str, row_id: int) -> None:
    """
    Delete a row from a MySQL database table based on the row ID.

    Args:
        table_name (str): The name of the table.
        db_name (str): The name of the database.
        row_id (int): The ID of the row to delete.
    """
    engine = create_engine_and_connect(db_name)
    if engine is None:
        return
    
    with engine.connect() as conn:
        # Check if row with the given ID exists
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name} WHERE id = :id"), {'id': row_id})
        if result.fetchone()[0] == 0:
            st.error(f"Row with ID {row_id} does not exist in {table_name}.")
            return

        # Delete the row
        print("Deleting ", row_id)
        conn.execute(text(f"DELETE FROM {table_name} WHERE id = :id"), {'id': row_id})
        st.cache_data.clear()

@st.cache_resource
def get_db_connection(db_name: str):
    return create_engine_and_connect(db_name)

@st.cache_data
def get_data(table_name: str, db_name: str) -> pd.DataFrame:
    return display_data(table_name, db_name)

# Streamlit UI
st.title("CS 338 Final Project")

# Sidebar for database options
with st.sidebar:
    db_option = st.selectbox("Select Database Type", ["Sample", "Production"])

# Hardcoded file paths
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
file_paths = {
    "Sample": os.path.join(project_root, "tables", "prod", "movie.csv"),
    "Production": os.path.join(project_root, "tables", "sample", "movie.csv")
}

# Get the chosen file path
file_path = file_paths[db_option]

# Use file name without extension as table name
table_name = os.path.basename(file_path).split('.')[0]

# Choose the appropriate database name
db_name = "sample_db" if db_option == "Sample" else "production_db"

# Load CSV to MySQL and display data automatically on page load
load_csv_to_mysql(file_path, table_name, db_name)

# Pagination parameters
rows_per_page = st.sidebar.number_input("Rows per page", min_value=1, value=10)
total_rows = get_total_rows(table_name, db_name)
total_pages = (total_rows + rows_per_page - 1) // rows_per_page
current_page = st.sidebar.number_input("Page number", min_value=1, max_value=total_pages, value=1)

# Calculate offset
offset = (current_page - 1) * rows_per_page

# Get paginated data
df = display_data(table_name, db_name, rows_per_page, offset)
st.dataframe(df, hide_index=True)

# Display total rows and pages
st.sidebar.write(f"Total rows: {total_rows}")
st.sidebar.write(f"Total pages: {total_pages}")

# Delete row section
row_id = st.number_input(f"Row ID to delete from {table_name}:", min_value=1, step=1)
if st.button(f"Delete Row {row_id} from {table_name}"):
    delete_row_from_table(table_name, db_name, row_id)
    st.success(f"Row {row_id} deleted from {table_name}")