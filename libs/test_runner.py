
import sqlite3
import matplotlib.pyplot as plt
import copy

from libs.helpers import db
from libs.helpers.mock_generator import Dipl_MockGenerator
from libs.helpers.utils import bytes_to_int
from libs.helpers.proj_config import default_sleep_s, db_tablename
from libs.kafka.json.consumer import Dipl_JsonConsumer
from libs.kafka.json.message import Dipl_JsonBatch, Dipl_JsonBatchInfo
from libs.kafka.json.producer import Dipl_JsonProducer


def create_test_run(
  type: str,
  mock_generator: Dipl_MockGenerator,
  reps_per_test_case: int
):

  # Publish 1 user in batch
  if type == 'small':
    for reps in range(reps_per_test_case):
      yield Dipl_JsonBatch(mock_generator, spawn_count=1)

  # Publish 100, 200, ..., 1000 users
  elif type == 'medium':
    for user_count in range(100, 1001, 100):
      for reps in range(reps_per_test_case):
        yield Dipl_JsonBatch(mock_generator, user_count)

  # Publish 2000, 3000, ..., 10000 users
  elif type == 'large':
    for user_count in range(2000, 10001, 1000):
      for reps in range(reps_per_test_case):
        yield Dipl_JsonBatch(mock_generator, user_count)

  # Publish 20000, 25000, ..., 40000 users
  elif type == 'extra_large':
    for user_count in range(20000, 40001, 5000):
      for reps in range(reps_per_test_case):
        yield Dipl_JsonBatch(mock_generator, user_count)


def run_all_tests(prod: Dipl_JsonProducer, mock_generator: Dipl_MockGenerator):

  reps = 10

  def callback(err, msg):
    if err is not None:
      prod.log(f'Failed to deliver message: {msg}: {err}')
    else:
      size_kb = len(msg) / 1024
      prod.log(f'Produced message {bytes_to_int(msg.key())} of size {round(size_kb, 2)}kB')

  prod.produce_queue = []
  for test_case in create_test_run('small', mock_generator, reps):
    prod.produce_queue.append(test_case)
  prod.log(f'Inserted {len(prod.produce_queue)} messages to producer queue.')
  prod.run(
    produce_callback=callback,
    sleep_amount=default_sleep_s
  )

  prod.produce_queue = []
  for test_case in create_test_run('medium', mock_generator, reps):
    prod.produce_queue.append(test_case)
  prod.log(f'Inserted {len(prod.produce_queue)} messages to producer queue.')
  prod.run(
    produce_callback=callback,
    sleep_amount=default_sleep_s
  )

  prod.produce_queue = []
  for test_case in create_test_run('large', mock_generator, reps):
    prod.produce_queue.append(test_case)
  prod.log(f'Inserted {len(prod.produce_queue)} messages to producer queue.')
  prod.run(
    produce_callback=callback,
    sleep_amount=default_sleep_s
  )

  prod.produce_queue = []
  for test_case in create_test_run('extra_large', mock_generator, reps):
    prod.produce_queue.append(test_case)
  prod.log(f'Inserted {len(prod.produce_queue)} messages to producer queue.')
  prod.run(
    produce_callback=callback,
    sleep_amount=default_sleep_s
  )



def monitor_tests(consumer: Dipl_JsonConsumer):

  print('Started test monitoring')

  def create_table(cursor: sqlite3.Cursor):
    cursor.execute(f'DROP TABLE IF EXISTS {db_tablename}')
    cursor.execute(f"""
      CREATE TABLE {db_tablename} (
        id INTEGER PRIMARY KEY,
        user_count INTEGER,
        size_kb REAL,
        ts_created REAL,
        ts_received REAL,
        consume_duration REAL,
        type TEXT
      );
    """)
  db.operate_on_db(create_table)
  print(f'Created table {db_tablename}')

  results: list[Dipl_JsonBatchInfo] = []
  def consume_callback(msg: Dipl_JsonBatchInfo):
    consumer.log(f'consumed message {msg.id} of size {round(msg.size_kb, 2)}kB')
    results.append(msg)
  consumer.run(
    consume_callback
  )

  def insert_results(cursor: sqlite3.Cursor):
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
          'json'
        );
      """)
  db.operate_on_db(insert_results)
  consumer.log(f'Inserted {len(results)} rows of JSON results.')

  # Now show the results


def show_results():

  results = []
  def select_data_from_db(cursor: sqlite3.Cursor):
    query = f"""
      SELECT
        user_count,
        AVG(consume_duration) as avg_consume_duration,
        COUNT(*) as sample_size
      FROM {db_tablename}
      GROUP BY user_count
    """
    cursor.execute(query)
    output = cursor.fetchall()
    results = output
  db.operate_on_db(select_data_from_db)

  # Show results
  x_axis = [res.user_count for res in results_sorted]
  y_axis = [res.consume_duration for res in results_sorted]

  plt.bar(x_axis, y_axis, color='skyblue', edgecolor='black')
  plt.xlabel('User count')
  plt.ylabel('Consume duration')
  plt.title('User count vs Consume duration')

  plt.show()
