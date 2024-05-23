# Install required libraries:
#   pip install confluent-kafka colorama tqdm

import time

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

  def on_loop_end(producer):
    producer.is_active = producer.produced_count < received_args.produce_count
    sleep_duration = 0.5
    time.sleep(sleep_duration)

  producer_config = {
    'bootstrap.servers': received_args.bootstrap_server,
    'message.max.bytes': 10_000_000,  # 10 MB should be cca spawn_count=60000, but max seems to be spawn_count=45000
    # 'message.max.bytes': 975_000,
    ## 'message.max.bytes': 250_000_000,
    ### 'fetch.message.max.bytes': 169_086_277,
  }

  Dipl_Producer(
    mock_generator=mocks,
    spawn_count=received_args.spawn_count,
    produce_callback=lambda producer, err, msg: None,
    on_loop_end=on_loop_end,
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
