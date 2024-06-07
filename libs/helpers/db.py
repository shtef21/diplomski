import sqlite3

from libs.kafka.message import Dipl_BatchInfo
from .proj_config import db_filename, db_tablename
from pprint import pprint


def __operate_on_db(what_to_do):
  try:
    # Connect to DB and create cursor
    sqlite_conn = sqlite3.connect(db_filename)
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
    print('sqlite3.Error occurred -', error)

  # Close DB Connection irrespective of success or failure
  finally:
    if sqlite_conn:
      sqlite_conn.close()
      print('SQLite connection closed.')


def create_stats_table():
  def _create_table(cursor: sqlite3.Cursor):
    cursor.execute(f"""
      CREATE TABLE IF NOT EXISTS {db_tablename} (
        id INTEGER PRIMARY KEY,
        user_count INTEGER,
        size_kb REAL,
        ts_created REAL,
        ts_received REAL,
        consume_duration REAL,
        type TEXT
      );
    """)
  __operate_on_db(_create_table)


def insert_results(results: list[Dipl_BatchInfo]):
  def _insert_results(cursor: sqlite3.Cursor):
    for res in results:
      cursor.execute(f"""
        INSERT INTO {db_tablename}
        VALUES (
          {res.id},
          {res.user_count},
          {res.size_kb},
          {res.ts_created},
          {res.ts_received},
          {res.consume_duration},
          '{res.type}'
        );
      """)
  __operate_on_db(_insert_results)


def select_arr(query) -> list[any]:
  query_results = []
  def _get_results(cursor: sqlite3.Cursor):
    nonlocal query_results
    cursor.execute(f"""
      SELECT
        user_count,
        AVG(consume_duration) as cduration_avg,
        SUM(
          (consume_duration-(SELECT AVG(consume_duration) FROM {db_tablename}))
          * (consume_duration-(SELECT AVG(consume_duration) FROM {db_tablename}))
        ) / (COUNT(consume_duration)-1)
        AS cduration_variance
      FROM {db_tablename}
      GROUP BY user_count
    """)
    query_results = cursor.fetchall()
  __operate_on_db(_get_results)
  return query_results


def show_db_version(cursor: sqlite3.Cursor):
  # Write a query and execute it with cursor
  query = 'select sqlite_version();'
  cursor.execute(query)

  # Fetch and output result
  result = cursor.fetchone()
  print(f'> SQLite version is {result[0]}')


def select_data_from_db(cursor: sqlite3.Cursor):
  query = f'SELECT * FROM {proj_config.db_tablename}'
  cursor.execute(query)
  output = cursor.fetchall()
  print(f'> Fetched {len(output)} rows. Take a look at first 5:')
  print('-' * 50)
  pprint(output[:5])
  print('-' * 50)
