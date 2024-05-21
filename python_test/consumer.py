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


class Dipl_Consumer:

  def __init__(self, consume_callback):
    self.is_active = False
    self.consume_callback = consume_callback

  
  # log function
  def log(self, *args, **kwargs):
    print(
      Back.RED + Fore.WHITE + 'Consumer:' + Style.RESET_ALL,
      *args,
      **kwargs
    )


  def consume_wrapper(self, msg):
    size_kb = len(msg) / 1024
    msg_key = msg.key().decode('utf-8') if msg.key() else None
    id = None
    created_timestamp = None
    read_timestamp = time.time()
    consume_duration = None
    # data = dipl_utils.parse_json_str(msg_utf8)
    
    if msg_key and '_' in msg_key:
      key_data = msg_key.split('_')
      id = int(key_data[0])
      created_timestamp = float(key_data[1])
      consume_duration = read_timestamp - created_timestamp
      self.log(
        f'Received message batch (id={id})',
        f'of size {round(size_kb, 2)}kB',
        f'in {round(consume_duration, 4)}s'
      )
    else:
      self.log(
        f'Received message batch of unknown format.',
        f'size={round(size_kb, 2)}kB',
        f'timestamp={read_timestamp}s',
        f'key={msg_key}',
        f'value={msg.value()}'
      )

    info = {
      'id': id,
      'size_kb': size_kb,
      'created_timestamp': created_timestamp,
      'received_timestamp': read_timestamp,
      'consume_duration_s': consume_duration,
    }
    self.consume_callback(self, info)


  def run(self, bootstrap_server, topic_name):

    topics_to_consume = [ topic_name ]
    try:
      # TODO: fix max size
      # TODO: only look for msgs after consumer was initialized
      consumer = Consumer({
      'bootstrap.servers': bootstrap_server,
      'group.id': proj_config.string_consumer_group_id,
      'message.max.bytes': 250_000_000,
      # 'fetch.message.max.bytes': 250_086_277,
      })
      consumer.subscribe(topics_to_consume)
      self.log(f"I'm up!  Listening to {topics_to_consume} until exit or b'stop_consume' message.")

      self.is_active = True
      poll_timeout = 30.0

      while self.is_active:
        self.log(f'Polling data ({poll_timeout}s timeout)...')
        msg = consumer.poll(timeout=poll_timeout)

        if msg is None:
          continue

        if msg.error():
          if msg.error().code() == KafkaError._PARTITION_EOF:
            # End of partition event
            self.log(f'%{msg.topic()} [{msg.partition()}] reached end at offset {msg.offset()}\n')
          else:
            raise KafkaException(msg.error())

        else:
          if msg.value() == b'stop_consume':
            self.log(f'Received stop_consume message.')
            self.is_active = False

          else:
            self.consume_wrapper(msg)
            # timer.add_custom_timestamp(created_timestamp, f'create_batch_{id}')
            # timer.add_custom_timestamp(read_timestamp, f'received_batch_{id}')

    finally:
      # Close down consumer to commit final offsets.
      consumer.close()
