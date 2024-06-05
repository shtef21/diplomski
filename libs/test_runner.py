
import sqlite3
from typing import Generator

from python_test.helpers.mock_generator import Dipl_MockGenerator
from python_test.helpers.utils import bytes_to_int
from python_test.helpers.proj_config import default_sleep_s
from python_test.kafka.message import Dipl_MessageBatch
from python_test.kafka.producer import Dipl_Producer


def create_test_run(
  type: str,
  mock_generator: Dipl_MockGenerator,
  reps_per_test_case: int
):

  # Publish 1 user in batch
  if type == 'small':
    for reps in range(reps_per_test_case):
      yield Dipl_MessageBatch(mock_generator, spawn_count=1)

  # Publish 100, 200, ..., 1000 users
  elif type == 'medium':
    for user_count in range(100, 1001, 100):
      for reps in range(reps_per_test_case):
        yield Dipl_MessageBatch(mock_generator, user_count)

  # Publish 2000, 3000, ..., 10000 users
  elif type == 'large':
    for user_count in range(2000, 10001, 1000):
      for reps in range(reps_per_test_case):
        yield Dipl_MessageBatch(mock_generator, user_count)

  # Publish 20000, 25000, ..., 40000 users
  elif type == 'extra_large':
    for user_count in range(20000, 40001, 5000):
      for reps in range(reps_per_test_case):
        yield Dipl_MessageBatch(mock_generator, user_count)



def run_all_tests(prod: Dipl_Producer, mock_generator: Dipl_MockGenerator):

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

