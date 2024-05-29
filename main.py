# Install required libraries:
#   pip install confluent-kafka colorama tqdm

import time

from python_test.helpers.utils import bytes_to_int
from python_test.kafka.message import Dipl_MessageBatch
from python_test.kafka.producer import Dipl_Producer
from python_test.kafka.consumer import Dipl_Consumer
from python_test.helpers.mock_generator import Dipl_MockGenerator
from python_test.helpers.proj_config import arg_parser, default_sleep_s
from python_test.test_runner import create_test_run, run_all_tests


# Setup args
received_args = arg_parser.parse_args()

# Mocked data handling
mock_generator = Dipl_MockGenerator(
  overwrite_prev=received_args.reset_mocks,
  show_logs=received_args.show_logs,
)


# Start up the producer or consumer
if received_args.is_producer:

  producer = Dipl_Producer(received_args.bootstrap_server, received_args.topic_name)
  run_all_tests(producer, mock_generator)


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
