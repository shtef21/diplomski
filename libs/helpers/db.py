
import os
import sqlite3
from typing import Callable, Any

from libs.models.stats import Dipl_StatsList


from ..models.measurement import Dipl_ConsumerMeasurement, Dipl_ProducerMeasurement
from .proj_config import default_db_path, db_tablename
from pprint import pprint


def __operate_on_db(what_to_do: Callable[[sqlite3.Cursor], None], custom_db: str = None):

  if custom_db and os.path.exists(custom_db) == False:
    raise Exception(f"Cannot find DB: {custom_db}")
  successful_operation = False
  
  try:
    conn_db = default_db_path if not custom_db else custom_db

    # Connect to DB and create cursor
    sqlite_conn = sqlite3.connect(conn_db)
    cursor = sqlite_conn.cursor()

    # Give cursor to the lambda
    what_to_do(cursor)

    # Commit operation
    sqlite_conn.commit()

    # Close the cursor
    cursor.close()
    successful_operation = True

  except sqlite3.Error as error:
    print('sqlite3.Error occurred -', error)

  # Close DB Connection irrespective of success or failure
  finally:
    if sqlite_conn:
      sqlite_conn.close()
  return successful_operation


def initialize_database():
  def _create_table(cursor: sqlite3.Cursor):
    cursor.execute(f"""
      CREATE TABLE IF NOT EXISTS {db_tablename} (
        batch_id INTEGER PRIMARY KEY,
        type TEXT NOT NULL,
        user_count INTEGER NOT NULL,
        produced_size_kb REAL NOT NULL,
        ts0_generated REAL NOT NULL,
        ts1_serialized REAL NOT NULL,
        ts2_produced REAL NOT NULL,
        ts3_created REAL,
        ts4_consumed REAL,
        ts5_deserialized REAL,
        consumed_size_kb REAL,
        serialize_duration REAL GENERATED ALWAYS AS (ts1_serialized - ts0_generated) VIRTUAL,
        produce_duration REAL GENERATED ALWAYS AS (ts2_produced - ts1_serialized) VIRTUAL,
        consume_duration REAL GENERATED ALWAYS AS (ts4_consumed - ts3_created) VIRTUAL,
        deserialize_duration REAL GENERATED ALWAYS AS (ts5_deserialized - ts4_consumed) VIRTUAL,
        throughput_kbps REAL GENERATED ALWAYS AS (
          CASE WHEN ts4_consumed - ts3_created > 0
          THEN (consumed_size_kb / (ts4_consumed - ts3_created))
          ELSE 0 END
        ) VIRTUAL
      );
    """)
  is_ok = __operate_on_db(_create_table)
  return is_ok


def insert_producer_msmts(msmts: list[Dipl_ProducerMeasurement]):
  def _insert_prod_msmts(cursor: sqlite3.Cursor):
    for m in msmts:
      cursor.execute(f"""
        INSERT INTO {db_tablename} (
          batch_id,
          type,
          user_count,
          produced_size_kb,
          ts0_generated,
          ts1_serialized,
          ts2_produced
        )
        VALUES (
          {m.batch_id},
          '{m.type}',
          {m.user_count},
          {m.produced_size_kb},
          {m.ts0_generated},
          {m.ts1_serialized},
          {m.ts2_produced}
        );
      """)
  __operate_on_db(_insert_prod_msmts)


def update_consumer_msmts(msmts: list[Dipl_ConsumerMeasurement]):
  def _update_msmts(cursor: sqlite3.Cursor):
    for m in msmts:
      cursor.execute(f"""
        UPDATE {db_tablename}
        SET
          ts3_created = {m.ts3_created},
          ts4_consumed = {m.ts4_consumed},
          ts5_deserialized = {m.ts5_deserialized},
          consumed_size_kb = {m.consumed_size_kb}
        WHERE
          batch_id = {m.batch_id};
      """)
  __operate_on_db(_update_msmts)



def calculate_stats(custom_db_path: str = None) -> Dipl_StatsList:
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

