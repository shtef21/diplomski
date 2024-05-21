import time
from confluent_kafka import Consumer, KafkaError, KafkaException, TIMESTAMP_CREATE_TIME
from colorama import Fore, Style, Back
from python_test.helpers import proj_config


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
    read_timestamp = time.time()
    size_kb = len(msg) / 1024
    id = None if not msg.key() else int(msg.key().decode('utf-8'))
    ts_type, ts_milliseconds = msg.timestamp()
    created_timestamp = -1 if ts_type != TIMESTAMP_CREATE_TIME else ts_milliseconds / 1000
    consume_duration = -1 if ts_type != TIMESTAMP_CREATE_TIME else read_timestamp - created_timestamp
    # data = dipl_utils.parse_json_str(msg_utf8)

    info = {
      'id': id,
      'size_kb': size_kb,
      'created_timestamp': created_timestamp,
      'received_timestamp': read_timestamp,
      'consume_duration_s': consume_duration,
      'value': msg.value() if not id else 'TLDR;',
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
      poll_timeout = 5.0

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

    finally:
      # Close down consumer to commit final offsets.
      consumer.close()
