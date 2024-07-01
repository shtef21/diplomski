import time
from confluent_kafka import Consumer, KafkaError, KafkaException, TIMESTAMP_CREATE_TIME
from colorama import Fore, Style, Back
from typing import Callable

from ...helpers.utils import bytes_to_int, json_to_data
from ...helpers.proj_config import consumer_group_json, max_msg_size, topic_name_json, topic_name_info
from ...models.measurement import Dipl_ConsumerMeasurement


class Dipl_JsonConsumer:

  def __init__(self, bootstrap_server):
    self.is_active = False
    self.config = {
      'bootstrap.servers': bootstrap_server,
      'group.id': consumer_group_json,
      'message.max.bytes': max_msg_size,
    }

  # log function
  def log(self, *args, **kwargs):
    print(
      Back.RED + Fore.WHITE + 'J_Consumer:' + Style.RESET_ALL,
      *args,
      **kwargs
    )

  def run(self, consume_callback: Callable[[Dipl_ConsumerMeasurement], None]):

    topics_to_consume = [ topic_name_json, topic_name_info ]
    try:
      consumer = Consumer(self.config)
      consumer.subscribe(topics_to_consume)
      self.log(f"I'm up!  Listening to {topics_to_consume}. (^C to exit)")

      self.is_active = True
      poll_timeout = 1.0

      while self.is_active:
        # Await data for poll_timeout seconds
        msg = consumer.poll(timeout=poll_timeout)

        if msg is None:
          continue

        elif msg.error():
          if msg.error().code() == KafkaError._PARTITION_EOF:
            # End of partition event
            self.log(f'%{msg.topic()} [{msg.partition()}] reached end at offset {msg.offset()}\n')
          else:
            raise KafkaException(msg.error())

        else:
          if msg.topic() == topic_name_json:
            batch_id = bytes_to_int(msg.key())
            msmt = Dipl_ConsumerMeasurement(batch_id)
            msmt.consumed_size_kb = len(msg) / 1024

            ts_type, ts_milliseconds = msg.timestamp()
            if ts_type == TIMESTAMP_CREATE_TIME:
              msmt.ts3_created = ts_milliseconds / 1000

            msmt.ts4_consumed = time.time()

            data = json_to_data(msg.value().decode('utf-8'))
            # self.log(f'Fetched {len(data)} users.')

            msmt.ts5_deserialized = time.time()
            consume_callback(msmt)
          elif msg.topic() == topic_name_info:
            self.log(f'Received INFO message: {msg.value().decode("utf-8")}')
          else:
            # Only happens if topics_to_consume has many topics
            self.log(f'Non-standard message received:')
            self.log(msg.value())

    except KeyboardInterrupt:
      self.log('^C')
    finally:
      # Close down consumer to commit final offsets.
      consumer.close()
      self.log("Done consuming.")
