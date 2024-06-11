
import sqlite3
import matplotlib.pyplot as plt
import copy

from .kafka.proto.proto_consumer import Dipl_ProtoConsumer
from .helpers import db
from .helpers.mock_generator import Dipl_MockGenerator
from .helpers.utils import bytes_to_int
from .helpers.proj_config import default_prod_sleep, db_tablename
from .kafka.json.consumer import Dipl_JsonConsumer
from .kafka.proto.proto_consumer import Dipl_ProtoConsumer
from .models.message import Dipl_JsonBatch, Dipl_BatchInfo, Dipl_ProtoBatch
from .kafka.json.producer import Dipl_JsonProducer
from .kafka.proto.proto_producer import Dipl_ProtoProducer


def create_test_run(
  type: str,
  mock_generator: Dipl_MockGenerator,
  reps_per_test_case: int,
  Dipl_BatchClass,
):

  # Publish 1 user in batch
  if type == 'small':
    for reps in range(reps_per_test_case):
      yield Dipl_BatchClass(mock_generator, spawn_count=1)

  # Publish 100, 200, ..., 1000 users
  elif type == 'medium':
    for user_count in range(100, 1001, 100):
      for reps in range(reps_per_test_case):
        yield Dipl_BatchClass(mock_generator, user_count)

  # Publish 2000, 3000, ..., 10000 users
  elif type == 'large':
    for user_count in range(2000, 10001, 1000):
      for reps in range(reps_per_test_case):
        yield Dipl_BatchClass(mock_generator, user_count)

  # Publish 20000, 25000, ..., 40000 users
  elif type == 'extra_large':
    for user_count in range(20000, 55001, 5000):
      for reps in range(reps_per_test_case):
        yield Dipl_BatchClass(mock_generator, user_count)



def run_all_tests(
  j_prod: Dipl_JsonProducer,
  p_prod: Dipl_ProtoProducer,
  mock_generator: Dipl_MockGenerator
):
  reps = 10

  def callback(prod, err, msg):
    if err is not None:
      prod.log(f'Failed to deliver message: {msg}: {err}')
    else:
      size_kb = len(msg) / 1024
      prod.log(f'Produced message {bytes_to_int(msg.key())} of size {round(size_kb, 2)}kB')

  def run_test(prod, test_size, batch_class):
    prod.produce_queue = []
    for test_case in create_test_run(test_size, mock_generator, reps, batch_class):
      prod.produce_queue.append(test_case)
    prod.log(f'Inserted {len(prod.produce_queue)} messages to producer queue.')
    prod.run(
      produce_callback=lambda err, msg: callback(prod, err, msg),
      sleep_amount=default_prod_sleep
    )

  run_test(j_prod, 'small', Dipl_JsonBatch)
  run_test(p_prod, 'small', Dipl_ProtoBatch)

  run_test(j_prod, 'medium', Dipl_JsonBatch)
  run_test(p_prod, 'medium', Dipl_ProtoBatch)

  run_test(j_prod, 'large', Dipl_JsonBatch)
  run_test(p_prod, 'large', Dipl_ProtoBatch)

  run_test(j_prod, 'extra_large', Dipl_JsonBatch)
  run_test(p_prod, 'extra_large', Dipl_ProtoBatch)



def monitor_tests(cons: Dipl_JsonConsumer | Dipl_ProtoConsumer, dry_run: bool = False):

  consumer_type = 'JSON' if type(cons) == Dipl_JsonConsumer else 'PROTO'
  print(f'Started {consumer_type} test monitoring')

  results: list[Dipl_BatchInfo] = []
  def consume_callback(msg: Dipl_BatchInfo):
    cons.log(f'Consumed msg {msg.id} of size {round(msg.size_kb, 2)}kB in {round(msg.consume_duration * 1000)}ms')
    results.append(msg)
  cons.run(
    consume_callback
  )

  if not dry_run:
    db.insert_results(results)
    cons.log(f'Inserted {len(results)} rows of {consumer_type} results.')
  else:
    cons.log(f'Dry run specified. Ignoring {len(results)} rows {consumer_type} results.')





def show_stats(stats_path: str):

  results = db.calculate_stats(stats_path)
  
  if len(results) == 0:
    print('Found 0 rows. Cannot show stats.')
    return

  user_counts = [
    str(row.user_count).replace('0000','0K').replace('000', 'K')
    for row in results
  ] 
  y_consume_time = [row.consume_duration_average * 1000 for row in results]
  sizes_kb_avg = [row.size_kb_avg for row in results]  # TODO: Add size above bars?
  # TODO: somehow display variance in durations? with opacity? with many bars?

  # Set size and grid
  plt.figure(figsize=(12, 3), frameon=True)
  plt.grid()

  # Mock two types of bar charts
  for i in range(len(user_counts)):
    if results[i][1] == 'json':
      plt.bar(user_counts[i], y_consume_time[i], color='blue', width=0.4)
    elif results[i][1] == 'proto':
      plt.bar(user_counts[i], y_consume_time[i], color='maroon', width=0.5)

  plt.xlabel('Object count')
  plt.ylabel('Consume duration (ms)')
  plt.title('JSON (blue) vs PROTO (red) average consume duration')

  plt.show()

