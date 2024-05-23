import time
from confluent_kafka import Consumer, KafkaError, KafkaException, TIMESTAMP_CREATE_TIME
from colorama import Fore, Style, Back
from python_test.helpers import proj_config
from python_test.message import Dipl_MessageBatchInfo


class Dipl_Consumer:

  def __init__(self, consume_callback, **kwargs):
    self.is_active = False
    self.consume_callback = consume_callback
    self.kwargs = kwargs

  
  # log function
  def log(self, *args, **kwargs):
    print(
      Back.RED + Fore.WHITE + 'Consumer:' + Style.RESET_ALL,
      *args,
      **kwargs
    )


  def consume_wrapper(self, msg):
    info = Dipl_MessageBatchInfo(msg)
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
        # Await data (5s)
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
