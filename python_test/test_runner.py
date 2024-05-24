
import sqlite3
from typing import Generator

from python_test.helpers.mock_generator import Dipl_MockGenerator
from python_test.message import Dipl_MessageBatch


def create_test_run(
    type, mocks: Dipl_MockGenerator,
    reps_per_test_case = 10
  ) -> Generator[Dipl_MessageBatch, None, None]:

  # Publish 1 user in batch
  if type == 'small':
    for reps in range(reps_per_test_case):
      yield Dipl_MessageBatch(mocks, spawn_count=1)

  # Publish 100, 200, ..., 1000 users
  if type == 'medium':
    for user_count in range(100, 1001, 100):
      for reps in range(reps_per_test_case):
        yield Dipl_MessageBatch(mocks, user_count)

  # Publish 2000, 3000, ..., 10000 users
  if type == 'large':
    for user_count in range(2000, 10001, 1000):
      for reps in range(reps_per_test_case):
        yield Dipl_MessageBatch(mocks, user_count)

  # Publish 20000, 25000, ..., 40000 users
  if type == 'extra_large':
    for user_count in range(20000, 40001, 5000):
      for reps in range(reps_per_test_case):
        yield Dipl_MessageBatch(mocks, user_count)
