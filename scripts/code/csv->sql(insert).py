import csv
import os
import time


def csv_to_sql_insert(csv_file, table_name, chunk_size):

    with open(csv_file, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)


        headers = next(reader)
        columns = ', '.join(map(lambda x: f'"{x}"', headers))
        insert_template = f'INSERT INTO {table_name} ({columns}) VALUES\n'


        statements = []
        for row in reader:

            cleaned_row = [value.replace('null', '').strip() if value != 'NULL' else 'NULL' for value in row]


            # row_values = ', '.join(map(lambda x: f'"{x}"' if x != 'NULL' else 'NULL', cleaned_row))


            # row_values = ', '.join(f'"{value}"' if value != 'NULL' else 'NULL' for value in row)


            row_values = ', '.join(f'NULL' if value.upper() == 'NULL' else f'"{value}"' for value in row)


            statements.append(f'({row_values}),\n')


        chunked_statements = [statements[i:i + chunk_size] for i in range(0, len(statements), chunk_size)]


        sql_insert_statements = []
        for chunk in chunked_statements:
            sql_insert = insert_template + ''.join(chunk)[:-2] + ';\n'
            sql_insert_statements.append(sql_insert)

        return sql_insert_statements


def write_to_sql_files(sql_statements, base_path, table_name):

    for i, statement in enumerate(sql_statements, start=1):
        file_path = os.path.join(base_path, f'{table_name}-{i}.sql')
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            f.write(statement)
            # print(statement)
        print(f'Wrote {file_path}')



if __name__ == '__main__':

    start_time = time.time()

    base_path = r''
    file_name = 'ratings_small.csv'
    csv_file_path = os.path.join(base_path, file_name)
    table_name = 'ratings_small'
    chunk_size = 100000000

    sql_statements = csv_to_sql_insert(csv_file_path, table_name, chunk_size)


    write_to_sql_files(sql_statements, base_path, table_name)


    end_time = time.time()


    elapsed_time = end_time - start_time
    print(f'Elapsed time: {elapsed_time:.2f} seconds')

