
import sqlite3
import matplotlib.pyplot as plt
import copy

from .helpers import db
from .helpers.mock_generator import Dipl_MockGenerator
from .helpers.utils import bytes_to_int
from .helpers.proj_config import default_prod_sleep, db_tablename
from .kafka.json.consumer import Dipl_JsonConsumer
from .kafka.message import Dipl_JsonBatch, Dipl_BatchInfo, Dipl_ProtoBatch
from .kafka.json.producer import Dipl_JsonProducer
from .kafka.protobuf.proto_producer import Dipl_ProtoProducer


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



def run_json_tests(prod: Dipl_JsonProducer, mock_generator: Dipl_MockGenerator):

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
    sleep_amount=default_prod_sleep
  )

  prod.produce_queue = []
  for test_case in create_test_run('medium', mock_generator, reps):
    prod.produce_queue.append(test_case)
  prod.log(f'Inserted {len(prod.produce_queue)} messages to producer queue.')
  prod.run(
    produce_callback=callback,
    sleep_amount=default_prod_sleep
  )

  prod.produce_queue = []
  for test_case in create_test_run('large', mock_generator, reps):
    prod.produce_queue.append(test_case)
  prod.log(f'Inserted {len(prod.produce_queue)} messages to producer queue.')
  prod.run(
    produce_callback=callback,
    sleep_amount=default_prod_sleep
  )

  prod.produce_queue = []
  for test_case in create_test_run('extra_large', mock_generator, reps):
    prod.produce_queue.append(test_case)
  prod.log(f'Inserted {len(prod.produce_queue)} messages to producer queue.')
  prod.run(
    produce_callback=callback,
    sleep_amount=default_prod_sleep
  )



def monitor_json_tests(consumer: Dipl_JsonConsumer):

  print('Started test monitoring')

  db.create_stats_table()
  print(f'Created table {db_tablename}')

  results: list[Dipl_BatchInfo] = []
  def consume_callback(msg: Dipl_BatchInfo):
    consumer.log(f'consumed message {msg.id} of size {round(msg.size_kb, 2)}kB')
    results.append(msg)
  consumer.run(
    consume_callback
  )

  db.insert_results(results)
  consumer.log(f'Inserted {len(results)} rows of JSON results.')



def run_proto_tests(prod: Dipl_ProtoProducer, mock_generator: Dipl_MockGenerator):

  reps = 10

  def callback(err, msg):
    if err is not None:
      prod.log(f'Failed to deliver message: {msg}: {err}')
    else:
      size_kb = len(msg) / 1024
      prod.log(f'Produced message {bytes_to_int(msg.key())} of size {round(size_kb, 2)}kB')

  prod.produce_queue = []
  prod.produce_queue.append(Dipl_ProtoBatch(mock_generator, 100))
  prod.log(f'Inserted {len(prod.produce_queue)} messages to producer queue.')
  prod.run(
    produce_callback=callback,
    sleep_amount=default_prod_sleep
  )



def show_stats():

  results = db.select_arr(f"""
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

  user_counts = [
    str(row[0]).replace('0000','0K').replace('000', 'K')
    for row in results
  ]
  y_consume_time = [row[1] for row in results]

  plt.figure(figsize=(10, 6))
  # plt.bar(user_counts, y_consume_time, color='skyblue', width=0.4)

  # Mock two types of bar charts
  for i in range(len(user_counts)):
    if i % 2 == 0:
      plt.bar(user_counts[i], y_consume_time[i], color='blue', width=0.4)
    else:
      plt.bar(user_counts[i], y_consume_time[i], color='maroon', width=0.4)

  plt.xlabel('User count')
  plt.ylabel('Consume duration')
  plt.title('User count vs Consume duration')

  plt.show()

