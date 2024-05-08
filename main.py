# pip install confluent-kafka

import time
from confluent_kafka import Consumer, Producer, KafkaError, KafkaException
from colorama import Fore, Style, Back
from pprint import pprint

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
    consumer = Consumer({
      'bootstrap.servers': proj_config.bootstrap_server,
      'group.id': proj_config.string_consumer_group_id
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
          log(
            '%% %s [%d] reached end at offset %d\n' %
            (msg.topic(), msg.partition(), msg.offset())
          )
        elif msg.error():
          raise KafkaException(msg.error())
      else:
        msg_utf8 = msg.value().decode('utf-8')
        log(f'Received the following message: {msg_utf8}')
        if msg_utf8 == 'stop_consume':
          consumer_active = False

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
      log('Message produced: {1}'.format(msg.key(), msg.value()))

  producer = Producer({
    'bootstrap.servers': proj_config.bootstrap_server
  })
  produced_count = 0
  max_produced_count = received_args.produce_count
  log("I'm up! Producing started...")

  while produced_count < max_produced_count:
    data = mocks.get_many_users(10)
    message_batch = Dipl_MessageBatch(data)

    message_batch.set_start_timestamp()
    producer.produce(
      topic=proj_config.topic_name,
      #key=some_key,
      value=message_batch.to_json(),
      callback=producer_logger,
    )
    producer.flush()  # produce it synchronously
    produced_count += 1

    log(f'Produced {produced_count}/{max_produced_count} messages')
    log('Sleeping for 2.5s ...')
    time.sleep(2.5)

  producer.produce(
    topic=proj_config.topic_name,
    value='stop_consume',
    callback=producer_logger,
  )
  producer.flush()


# Start up the producer and/or consumer
if received_args.is_producer:
  print('Loading producer...')
  run_producer()
elif received_args.is_consumer:
  print('Loading consumer...')
  run_consumer()


# TODO: Use 'seaborn' for visualizing data (not matplotlib)?
pprint(timer.timestamps)
