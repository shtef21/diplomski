# Install required libraries:
#   pip install confluent-kafka colorama tqdm

import time

from python_test.helpers.utils import bytes_to_int
from python_test.message import Dipl_MessageBatch
from python_test.producer import Dipl_Producer
from python_test.consumer import Dipl_Consumer
from python_test.helpers.mock_generator import Dipl_MockGenerator
from python_test.helpers.proj_config import arg_parser, default_sleep_s
from python_test.test_runner import create_test_run


# Setup args
received_args = arg_parser.parse_args()


# Mocked data handling
mocks = Dipl_MockGenerator(
  overwrite_prev=received_args.reset_mocks,
  show_logs=received_args.show_logs,
)

if received_args.show_logs:
  mocks.show_some_data()



# Start up the producer and/or consumer
if received_args.is_producer:

  prod = Dipl_Producer()
  prod_config = {
      'bootstrap.servers': received_args.bootstrap_server,
      # 10 MB should be cca spawn_count=60000,
      # but max seems to be spawn_count=45000
      'message.max.bytes': 10_000_000,
    }

  def on_produce(err, msg):
    if err is not None:
      prod.log(f'Failed to deliver message: {msg}: {err}')
    else:
      size_kb = len(msg) / 1024
      prod.log(f'Produced message {bytes_to_int(msg.key())} of size {round(size_kb, 2)}kB')


  prod.produce_queue = []
  for test_case in create_test_run(type='small', mocks=mocks):
    prod.produce_queue.append(test_case)
    prod.log(f'Generated {test_case.spawn_count} users.')
  prod.run(
    config=prod_config,
    topic_name=received_args.topic_name,
    on_produce=on_produce,
    sleep_time=default_sleep_s
  )

  prod.produce_queue = []
  for test_case in create_test_run(type='medium', mocks=mocks):
    prod.produce_queue.append(test_case)
    prod.log(f'Generated {test_case.spawn_count} users.')
  prod.run(
    config=prod_config,
    topic_name=received_args.topic_name,
    on_produce=on_produce,
    sleep_time=default_sleep_s
  )

  prod.produce_queue = []
  for test_case in create_test_run(type='large', mocks=mocks):
    prod.produce_queue.append(test_case)
    prod.log(f'Generated {test_case.spawn_count} users.')
  prod.run(
    config=prod_config,
    topic_name=received_args.topic_name,
    on_produce=on_produce,
    sleep_time=default_sleep_s
  )

  ## Too large for now
  # prod.produce_queue = []
  # for test_case in create_test_run(type='extra_large', mocks=mocks):
  #   prod.produce_queue.append(test_case)
  #   prod.log(f'Generated {test_case.spawn_count} users.')
  # prod.run(
  #   config=prod_config,
  #   topic_name=received_args.topic_name,
  #   on_produce=on_produce,
  #   sleep_time=default_sleep_s
  # )
  


elif received_args.is_consumer:
  print('Loading consumer...')

  def on_consumed(consumer, info):
    consumer.log(info)

  Dipl_Consumer(
    consume_callback=on_consumed,
  ).run(
    bootstrap_server=received_args.bootstrap_server,
    topic_name=received_args.topic_name,
  )


# TODO: Use 'seaborn' for visualizing data (not matplotlib)?
