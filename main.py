# pip install confluent-kafka

from confluent_kafka import Consumer, Producer, KafkaError, KafkaException
from colorama import Fore, Style, Back
import argparse
import time

import python_test.helpers.utils as dipl_utils
from python_test.helpers.mock_generator import MockGenerator
from python_test.helpers import proj_config
from python_test.helpers.clock import Dipl_Clock


# Command line handling
arg_parser = argparse.ArgumentParser(description="Kafka communication code")
arg_parser.add_argument(
  '--reset-mocks',
  dest='reset_mocks',
  action='store_true',
  help='If sent, mocked data will be generated even if it already exists'
)
arg_parser.add_argument(
  '--producer-only',
  dest='producer_only',
  action='store_true',
  help='If sent, only loads up the producer'
)
arg_parser.add_argument(
  '--consumer-only',
  dest='consumer_only',
  action='store_true',
  help='If sent, only loads up the consumer'
)
received_args = arg_parser.parse_args()


# Timer setup
timer = Dipl_Clock()
timer.start()


# Mocked data handling
mocks = MockGenerator(
  overwrite_prev=received_args.reset_mocks,
  show_logs=True
)
timer.add_timestamp('mock_generate')
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

  topics_to_consumer = [ proj_config.topic_name ]
  try:
    consumer = Consumer({
      'bootstrap.servers': proj_config.bootstrap_server,
      'group.id': proj_config.string_consumer_group_id
    })
    consumer_active = True
    log(f"I'm up!  Listening to {topics_to_consumer}...")

    while consumer_active:
      # Wait for a message up to 5 second
      log('Polling data (5s timeout)...')
      msg = consumer.poll(timeout=5.0)

      if msg is None:
        log('No data found.')
        continue
      else:
        log('Data found.')

      if msg.error():
        if msg.error().code() == KafkaError._PARTITION_EOF:
          # End of partition event
          log(
            '%% %s [%d] reached end at offset %d\n' %
            (msg.topic(), msg.partition(), msg.offset())
          )
        else:
          raise KafkaException(msg.error())
      else:
        if msg.value() == 'stop_consume':
          consumer_active = False
        log(f'Received the following message: {msg.value()}')
    
  finally:
    # Close down consumer to commit final offsets.
    consumer.close()



# Producer handling
def run_producer():
  def log(*args, **kwargs):
    print(
      Back.BLUE + Fore.WHITE + 'Producer:' + Style.RESET_ALL,
      *args,
      **kwargs
    )
  def producer_logger(err, msg):
    if err is not None:
      log('Failed to deliver message: {0}: {1}'.format(msg, err))
    else:
      # TODO: test out msg.topic()
      log('Message produced: {0}={1}'.format(msg.key(), msg.value()))

  producer = Producer({
    'bootstrap.servers': proj_config.bootstrap_server
  })
  produced_count = 0
  max_produced_count = 10
  log("I'm up! Producing started...")

  while produced_count < max_produced_count:
    data = mocks.get_many_users(10)
    json_value = dipl_utils.data_to_json(data)

    producer.produce(
      topic=proj_config.topic_name,
      #key=some_key,
      value=json_value,
      callback=producer_logger,
    )
    producer.flush()  # produce it synchronously
    produced_count += 1
    log('Sleeping for 2.5s ...')
    time.sleep(2.5)

  producer.produce(
    topic=proj_config.topic_name,
    value='stop_consume',
    callback=producer_logger,
  )


# Start up the producer and/or consumer
if received_args.consumer_only:
  print('Loading consumer...')
  run_consumer()

elif received_args.producer_only:
  print('Loading producer...')
  run_producer()

else:
  print(
    'Please run just the producer (--producer-only)',
    'or just the consumer (--consumer-only)'
  )


# TODO: Use 'seaborn' for visualizing data (not matplotlib)?
