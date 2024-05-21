# Install required libraries:
#   pip install confluent-kafka colorama tqdm

import time
from confluent_kafka import Consumer, Producer, KafkaError, KafkaException
from colorama import Fore, Style, Back
from pprint import pprint

from python_test.producer import Dipl_Producer
from python_test.consumer import Dipl_Consumer
import python_test.helpers.utils as dipl_utils
from python_test.helpers.mock_generator import MockGenerator
from python_test.helpers.proj_config import arg_parser
from python_test.helpers import proj_config
from python_test.helpers.clock import Dipl_Clock
from python_test.message import Dipl_MessageBatch


# Setup args
received_args = arg_parser.parse_args()


# Timer setup
timer = Dipl_Clock()
timer.start()


# Mocked data handling
mocks = MockGenerator(
  overwrite_prev=received_args.reset_mocks,
  show_logs=received_args.show_logs,
)
timer.add_timestamp('mock_generate')

if received_args.show_logs:
  mocks.show_some_data()
  timer.add_timestamp('mock_show')




# Start up the producer and/or consumer
if received_args.is_producer:

  def on_produced(producer, err, msg):
    if producer.produced_count > received_args.produce_count:
      producer.is_active = False

  def on_loop_end(producer):
    producer.log('Sleeping for 2.5s...')
    time.sleep(2.5)

  producer_config = {
    'bootstrap.servers': received_args.bootstrap_server,
    'message.max.bytes': 250_086_277,
    # 'fetch.message.max.bytes': 169_086_277,
  }

  Dipl_Producer(
    mock_generator=mocks,
    generate_count=5000,
    produce_callback=on_produced,
    on_loop_end=on_loop_end
  ).run(
    config=producer_config,
    topic_name=received_args.topic_name
  )


elif received_args.is_consumer:
  print('Loading consumer...')

  Dipl_Consumer(
    consume_callback=lambda consumer, info: consumer.log(info),
  ).run(
    bootstrap_server=received_args.bootstrap_server,
    topic_name=received_args.topic_name,
  )


# TODO: Use 'seaborn' for visualizing data (not matplotlib)?
pprint(timer.timestamps)
