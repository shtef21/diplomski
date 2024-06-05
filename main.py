# Install required libraries:
#   pip install confluent-kafka protobuf requests colorama tqdm matplotlib

import time

from libs.helpers.utils import bytes_to_int
from libs.kafka.json.message import Dipl_JsonBatch
from libs.kafka.json.producer import Dipl_JsonProducer
from libs.kafka.json.consumer import Dipl_JsonConsumer
from libs.helpers.mock_generator import Dipl_MockGenerator
from libs.helpers.proj_config import arg_parser, default_sleep_s
from libs.test_runner import monitor_tests, run_all_tests


# Setup args
received_args = arg_parser.parse_args()

# Mocked data handling
mock_generator = Dipl_MockGenerator()


# Start consumer
if received_args.is_producer:
  producer = Dipl_JsonProducer(received_args.bootstrap_server)
  run_all_tests(producer, mock_generator)

# Start producer
elif received_args.is_consumer:
  consumer = Dipl_JsonConsumer(received_args.bootstrap_server)
  monitor_tests(consumer)


# TODO: Use 'seaborn' for visualizing data (not matplotlib)?
