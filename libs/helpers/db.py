import sqlite3
from libs.helpers import proj_config
from pprint import pprint


def operate_on_db(what_to_do):
  try:
    # Connect to DB and create cursor
    sqlite_conn = sqlite3.connect(proj_config.db_filename)
    cursor = sqlite_conn.cursor()
    print('DB initialized.')

    # Give cursor to the lambda
    what_to_do(cursor)
    # Commit after every operation
    sqlite_conn.commit()

    # Close the cursor
    cursor.close()

  # Handle errors
  except sqlite3.Error as error:
    print('Error occurred -', error)

  # Close DB Connection irrespective of success or failure
  finally:
    if sqlite_conn:
      sqlite_conn.close()
      print('SQLite connection closed.')


def show_db_version(cursor: sqlite3.Cursor):
  # Write a query and execute it with cursor
  query = 'select sqlite_version();'
  cursor.execute(query)

  # Fetch and output result
  result = cursor.fetchone()
  print(f'> SQLite version is {result[0]}')


def create_table(cursor: sqlite3.Cursor):
  # Drop previous version
  cursor.execute(f'DROP TABLE IF EXISTS {proj_config.db_tablename}')

  # Create table
  table_definition = f"""
    CREATE TABLE {proj_config.db_tablename} (
      id INTEGER PRIMARY KEY,
      size_kb REAL,
      ts_created REAL,
      ts_received REAL,
      consume_duration REAL,
      type TEXT,
    );
  """
  cursor.execute(table_definition)
  print('> Table is ready')


def insert_data_to_db(cursor: sqlite3.Cursor):
  # Define some data
  data = [
    { 'size_kb': 1024, 'ts_received': 1000, 'ts_created': 900, 'consume_duration': 100 }
    for i in range(1000)
  ]

  # Create table
  for el in data:
    insert_query = f"""
      INSERT INTO {proj_config.db_tablename}
        (size_kb, ts_created, ts_received, consume_duration)
      VALUES (
        {el['size_kb']},
        {el['ts_created']},
        {el['ts_received']},
        {el['consume_duration']}
      );
    """
    cursor.execute(insert_query)
  print(f'> Inserted {len(data)} rows into {proj_config.db_tablename}')


def select_data_from_db(cursor: sqlite3.Cursor):
  query = f'SELECT * FROM {proj_config.db_tablename}'
  cursor.execute(query)
  output = cursor.fetchall()
  print(f'> Fetched {len(output)} rows. Take a look at first 5:')
  print('-' * 50)
  pprint(output[:5])
  print('-' * 50)


if __name__ == '__main__':
  operate_on_db(show_db_version)
  operate_on_db(create_table)
  operate_on_db(insert_data_to_db)
  operate_on_db(select_data_from_db)
