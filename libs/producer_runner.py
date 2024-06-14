
import time

from .helpers.mock_generator import Dipl_MockGenerator
from .helpers.proj_config import default_prod_sleep
from .models.message import Dipl_JsonBatch, Dipl_ProtoBatch
from .models.measurement import Dipl_ProducerMeasurement
from .kafka.json.json_producer import Dipl_JsonProducer
from .kafka.proto.proto_producer import Dipl_ProtoProducer


def create_test_run(
  type: str,
  mock_generator: Dipl_MockGenerator,
  reps_per_test_case: int,
  Dipl_BatchClass: Dipl_JsonBatch | Dipl_ProtoBatch,
):

  # Publish 1, 50, 100 users in batch
  if type == 'small':
    for user_count in [1, 50, 100]:
      for reps in range(reps_per_test_case):
        yield Dipl_BatchClass(mock_generator, user_count)

  # Publish 500, 1000 users
  elif type == 'medium':
    for user_count in [500, 1000]:
      for reps in range(reps_per_test_case):
        yield Dipl_BatchClass(mock_generator, user_count)

  # Publish 2500, 5000, 7500, 10000 users
  elif type == 'large':
    for user_count in [2500, 5000, 7500, 10000]:
      for reps in range(reps_per_test_case):
        yield Dipl_BatchClass(mock_generator, user_count)

  # Publish 25000, 40000, 55000 users
  elif type == 'extra_large':
    for user_count in [25000, 40000, 55000]:
      for reps in range(reps_per_test_case):
        yield Dipl_BatchClass(mock_generator, user_count)


def run_all_tests(
  j_prod: Dipl_JsonProducer,
  p_prod: Dipl_ProtoProducer,
  mock_generator: Dipl_MockGenerator,
  is_dry_run: bool,
):
  reps = 50
  measurements: list[Dipl_ProducerMeasurement] = []
  n_produced = 0

  def callback(
    prod: Dipl_JsonProducer | Dipl_ProtoProducer,
    msmt: Dipl_ProducerMeasurement,
    err,
    msg
  ):
    if err is not None:
      prod.log(f'Failed to deliver message: {msg}: {err}')
    else:
      msmt.ts2_produced = time.time()
      msmt.produced_size_kb = len(msg) / 1024
      measurements.append(msmt)


  def run_test(prod, test_size, batch_class):
    nonlocal n_produced
    prod.produce_queue = []
    for test_case in create_test_run(test_size, mock_generator, reps, batch_class):
      prod.produce_queue.append(test_case)
    prod.run(
      produce_callback=lambda msmt, err, msg: callback(prod, msmt, err, msg),
      sleep_amount=default_prod_sleep
    )
    n_produced += len(prod.produce_queue)

  j_prod.log('Running a small test.')
  run_test(j_prod, 'small', Dipl_JsonBatch)
  p_prod.log('Running a small test.')
  run_test(p_prod, 'small', Dipl_ProtoBatch)

  j_prod.log('Running a medium test.')
  run_test(j_prod, 'medium', Dipl_JsonBatch)
  p_prod.log('Running a medium test.')
  run_test(p_prod, 'medium', Dipl_ProtoBatch)

  j_prod.log('Running a large test.')
  run_test(j_prod, 'large', Dipl_JsonBatch)
  p_prod.log('Running a large test.')
  run_test(p_prod, 'large', Dipl_ProtoBatch)

  j_prod.log('Running an extra large test.')
  run_test(j_prod, 'extra_large', Dipl_JsonBatch)
  p_prod.log('Running an extra large test.')
  run_test(p_prod, 'extra_large', Dipl_ProtoBatch)

  wait_repetition = 5
  while wait_repetition > 0 and len(measurements) != n_produced:
    print(f'Waiting for measurements ({len(measurements)/{n_produced}})...')
    time.sleep(5.0)
    wait_repetition -= 1

  print('Done producing and measuring.')

  if len(measurements) != n_produced:
    missing_count = n_produced - len(measurements)
    print(f'Missing {missing_count} measurements.')

  if is_dry_run:
    print(f'Ignoring {len(measurements)} measurements.')
  else:
    print(f'Saving {len(measurements)} measurements.')
    # insert measurements to db...


