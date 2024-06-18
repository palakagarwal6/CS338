import csv
import os
import time

def csv_to_sql_insert(csv_file, table_name, chunk_size):
    # Open the CSV file for reading
    with open(csv_file, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)

        # Read the first row as headers and prepare the column list for the SQL statement
        headers = next(reader)
        columns = ', '.join(map(lambda x: f'"{x}"', headers))
        insert_template = f'INSERT INTO {table_name} ({columns}) VALUES\n'

        statements = []
        for row in reader:
            # Clean each row value, replacing 'null' with an empty string and stripping whitespace
            cleaned_row = [value.replace('null', '').strip() if value != 'NULL' else 'NULL' for value in row]

            # Prepare the row values for the SQL statement, handling NULL values properly
            row_values = ', '.join(f'NULL' if value.upper() == 'NULL' else f'"{value}"' for value in row)

            # Add the row values to the list of SQL statements
            statements.append(f'({row_values}),\n')

        # Split the statements into chunks to avoid creating overly large SQL insert statements
        chunked_statements = [statements[i:i + chunk_size] for i in range(0, len(statements), chunk_size)]

        sql_insert_statements = []
        for chunk in chunked_statements:
            # Combine the chunk into a single SQL insert statement
            sql_insert = insert_template + ''.join(chunk)[:-2] + ';\n'
            sql_insert_statements.append(sql_insert)

        return sql_insert_statements

def write_to_sql_files(sql_statements, base_path, table_name):
    # Write each SQL insert statement to a separate file
    for i, statement in enumerate(sql_statements, start=1):
        file_path = os.path.join(base_path, f'{table_name}-{i}.sql')
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            f.write(statement)
        print(f'Wrote {file_path}')

if __name__ == '__main__':
    start_time = time.time()

    base_path = r''
    file_name = 'ratings_small.csv'
    csv_file_path = os.path.join(base_path, file_name)
    table_name = 'ratings_small'
    chunk_size = 100000000

    # Convert CSV data to SQL insert statements
    sql_statements = csv_to_sql_insert(csv_file_path, table_name, chunk_size)

    # Write the SQL insert statements to files
    write_to_sql_files(sql_statements, base_path, table_name)

    end_time = time.time()

    # Calculate and print the elapsed time for the operation
    elapsed_time = end_time - start_time
    print(f'Elapsed time: {elapsed_time:.2f} seconds')
