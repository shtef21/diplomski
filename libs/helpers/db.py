import sqlite3
from typing import Callable, Any

from libs.models.stats import Dipl_StatsList


from ..models.message import Dipl_BatchInfo
from .proj_config import default_db_path, db_tablename
from pprint import pprint


def __operate_on_db(what_to_do: Callable[[sqlite3.Cursor], None], custom_db: str = None):
  try:
    # Connect to DB and create cursor
    conn_db = default_db_path if not custom_db else custom_db
    sqlite_conn = sqlite3.connect(conn_db)
    cursor = sqlite_conn.cursor()

    # Give cursor to the lambda
    what_to_do(cursor)

    # Commit operation
    sqlite_conn.commit()

    # Close the cursor
    cursor.close()

  except sqlite3.Error as error:
    print('sqlite3.Error occurred -', error)

  # Close DB Connection irrespective of success or failure
  finally:
    if sqlite_conn:
      sqlite_conn.close()


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



def calculate_stats(custom_db_path) -> Dipl_StatsList:
  query = f"""
      SELECT
        user_count,
        type,
        AVG(consume_duration) as consume_duration_average,
        SUM(
            (consume_duration-(SELECT AVG(consume_duration) FROM {db_tablename}))
            * (consume_duration-(SELECT AVG(consume_duration) FROM {db_tablename}))
          ) / (COUNT(consume_duration)-1)
          AS consume_duration_variance,
        AVG(size_kb) size_kb_avg
      FROM {db_tablename}
      GROUP BY user_count, type
      ORDER BY user_count, type
  """
  query_results = []

  def _get_results(cursor: sqlite3.Cursor):
    nonlocal query_results
    cursor.execute(query)
    query_results = cursor.fetchall()
  __operate_on_db(_get_results, custom_db_path)
  return Dipl_StatsList(query_results)


def show_db_version():
  result = None

  def _show_version(cursor: sqlite3.Cursor):
    nonlocal result
    cursor.execute('select sqlite_version()')
    result = cursor.fetchone()

  print(f'> SQLite version is {result[0]}')
  __operate_on_db(_show_version)

