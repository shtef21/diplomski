
from .helpers.mock_generator import Dipl_MockGenerator
from .helpers.proj_config import default_prod_sleep
from .models.message import Dipl_JsonBatch, Dipl_ProtoBatch
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
  mock_generator: Dipl_MockGenerator
):
  reps = 50

  def callback(prod: Dipl_JsonProducer | Dipl_ProtoProducer, err, msg):
    if err is not None:
      prod.log(f'Failed to deliver message: {msg}: {err}')
    else:
      size_kb = len(msg) / 1024
      # prod.log(f'Produced message {bytes_to_int(msg.key())} of size {round(size_kb, 2)}kB')

  def run_test(prod, test_size, batch_class):
    prod.produce_queue = []
    for test_case in create_test_run(test_size, mock_generator, reps, batch_class):
      prod.produce_queue.append(test_case)
    prod.run(
      produce_callback=lambda err, msg: callback(prod, err, msg),
      sleep_amount=default_prod_sleep
    )

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

  print('All tests done.')

