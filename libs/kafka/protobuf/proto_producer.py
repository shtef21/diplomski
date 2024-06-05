import time
from confluent_kafka import Producer
from colorama import Fore, Style, Back
from .message import Dipl_MessageBatch
from ...helpers.proj_config import default_sleep_s


class Dipl_Producer:

  def __init__(self, bootstrap_server, topic_name):
    self.produce_queue: list[Dipl_MessageBatch] = []
    self.config = {
      'bootstrap.servers': bootstrap_server,
      # 10 MB should be cca spawn_count=60000,
      # but max seems to be spawn_count=45000
      'message.max.bytes': 10_000_000,
    }
    self.topic_name = topic_name

  
  # log function
  def log(self, *args, **kwargs):
    print(
      Back.BLUE + Fore.WHITE + 'Producer:' + Style.RESET_ALL,
      *args,
      **kwargs
    )


  def run(self, produce_callback, sleep_amount):

    producer = Producer(self.config)
    self.log("I'm up! Producing started...")

    while len(self.produce_queue) > 0:
      message_batch = self.produce_queue.pop()
      producer.produce(
        topic = self.topic_name,
        key = message_batch.id_bytes,
        value = message_batch.data_json,
        callback = produce_callback,
      )

      producer.flush()  # produce it synchronously
      if sleep_amount > 0:
        time.sleep(default_sleep_s)

    self.log("Producer.produce_queue is empty. Producer done.")


