import time
from confluent_kafka import Producer
from colorama import Fore, Style, Back
from .message import Dipl_JsonBatch
from ...helpers.proj_config import default_sleep_s, topic_name_json


class Dipl_JsonProducer:

  def __init__(self, bootstrap_server):
    self.produce_queue: list[Dipl_JsonBatch] = []
    self.config = {
      'bootstrap.servers': bootstrap_server,
      # 10 MB should be cca spawn_count=60000,
      # but max seems to be spawn_count=45000
      'message.max.bytes': 10_000_000,
    }

  
  # log function
  def log(self, *args, **kwargs):
    print(
      Back.BLUE + Fore.WHITE + 'Producer:' + Style.RESET_ALL,
      *args,
      **kwargs
    )


  def run(self, produce_callback, sleep_amount=None):

    producer = Producer(self.config)
    self.log(f'Producing {len(self.produce_queue)} messages found in produce_queue...')

    while len(self.produce_queue) > 0:
      message_batch = self.produce_queue.pop()
      producer.produce(
        topic = topic_name_json,
        key = message_batch.id_bytes,
        value = message_batch.data_json,
        callback = produce_callback,
      )

      producer.flush()  # produce it synchronously
      if sleep_amount:
        if sleep_amount > 0:
          time.sleep(sleep_amount)
      else:
        time.sleep(default_sleep_s)

    self.log("Done producing.")


