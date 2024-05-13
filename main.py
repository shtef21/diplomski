# pip install confluent-kafka

import time
from confluent_kafka import Consumer, Producer, KafkaError, KafkaException
from colorama import Fore, Style, Back
from pprint import pprint

from python_test.producer import Dipl_Producer
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



# Consumer handling
def run_consumer():
  def log(*args, **kwargs):
    print(
      Back.RED + Fore.WHITE + 'Consumer:' + Style.RESET_ALL,
      *args,
      **kwargs
    )

  topics_to_consume = [ proj_config.topic_name ]
  try:
    # TODO: fix max size
    # TODO: only look for msgs after consumer was initialized
    consumer = Consumer({
      'bootstrap.servers': proj_config.bootstrap_server,
      'group.id': proj_config.string_consumer_group_id,
      'message.max.bytes': 250_086_277,
      # 'fetch.message.max.bytes': 250_086_277,
      # 'fetch.message.max.bytes': 250_086_277,
    })
    consumer.subscribe(topics_to_consume)
    log(f"I'm up!  Listening to {topics_to_consume}...")

    consumer_active = True
    while consumer_active:
      log('Polling data (2s timeout)...')
      msg = consumer.poll(timeout=2)

      if msg is None:
        log('No data found.')
        continue

      if msg.error():
        if msg.error().code() == KafkaError._PARTITION_EOF:
          # End of partition event
          log(f'%{msg.topic()} [{msg.partition()}] reached end at offset {msg.offset()}\n')

        elif msg.error():
          raise KafkaException(msg.error())
      else:
        size_kb = len(msg) / 1024
        msg_utf8 = msg.value().decode('utf-8')

        if msg_utf8 == 'stop_consume':
          log(f'Received stop_consume message.')
          consumer_active = False

        else:
          data = dipl_utils.parse_json_str(msg_utf8)
          key_data = [float(val) for val in msg.key().decode('utf-8').split('_')]
          id = key_data[0]
          created_timestamp = key_data[1]
          read_timestamp = time.time()
          diff = read_timestamp - created_timestamp
          
          log(f'Received message batch (id={id}) of size {round(size_kb, 2)}kB in {round(diff, 4)}s')
          # timer.add_custom_timestamp(created_timestamp, f'create_batch_{id}')
          # timer.add_custom_timestamp(read_timestamp, f'received_batch_{id}')

  finally:
    # Close down consumer to commit final offsets.
    consumer.close()



# Start up the producer and/or consumer
if received_args.is_producer:
  print('Loading producer...')

  def on_produced(producer, err, msg):
    if producer.produced_count > 5:
      producer.is_active = False

    if err is not None:
      producer.log('Failed to deliver message: {0}: {1}'.format(msg, err))
    else:
      producer.log('Message produced: {1}...'.format(msg.key(), msg.value()[:40]))

  def after_callback(producer):
    producer.log('Sleeping for 2.5s...')
    time.sleep(2.5)

  Dipl_Producer(
    mock_generator=mocks,
    generate_count=5000,
    produce_callback=on_produced,
    after_callback=after_callback
  ).run()


elif received_args.is_consumer:
  print('Loading consumer...')
  run_consumer()


# TODO: Use 'seaborn' for visualizing data (not matplotlib)?
pprint(timer.timestamps)
