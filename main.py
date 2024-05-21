# Install required libraries:
#   pip install confluent-kafka colorama tqdm

import time
from pprint import pprint

from python_test.producer import Dipl_Producer
from python_test.consumer import Dipl_Consumer
from python_test.helpers.mock_generator import MockGenerator
from python_test.helpers.proj_config import arg_parser


# Setup args
received_args = arg_parser.parse_args()


# Mocked data handling
mocks = MockGenerator(
  overwrite_prev=received_args.reset_mocks,
  show_logs=received_args.show_logs,
)

if received_args.show_logs:
  mocks.show_some_data()



# Start up the producer and/or consumer
if received_args.is_producer:

  def on_produced(producer, err, msg):
    msg_id = int(msg.key().decode('utf-8'))
    if producer.produced_count > received_args.produce_count:
      producer.is_active = False

  def on_loop_end(producer):
    sleep_duration = 0.25
    producer.log(f'Sleeping for {sleep_duration}s...')
    time.sleep(sleep_duration)

  producer_config = {
    'bootstrap.servers': received_args.bootstrap_server,
    'message.max.bytes': 250_086_277,
    # 'fetch.message.max.bytes': 169_086_277,
  }

  Dipl_Producer(
    mock_generator=mocks,
    spawn_count=received_args.spawn_count,
    produce_callback=on_produced,
    on_loop_end=on_loop_end
  ).run(
    config=producer_config,
    topic_name=received_args.topic_name
  )


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
