import time
from confluent_kafka import Producer
from colorama import Fore, Style, Back
from python_test.message import Dipl_MessageBatch
from .helpers.utils import int_to_bytes


class Dipl_Producer:

  def __init__(self):
    self.produce_queue: list[Dipl_MessageBatch] = []

  
  # log function
  def log(self, *args, **kwargs):
    print(
      Back.BLUE + Fore.WHITE + 'Producer:' + Style.RESET_ALL,
      *args,
      **kwargs
    )


  def run(self, **kwargs):

    producer = Producer(kwargs['config'])
    self.log("I'm up! Producing started...")

    while len(self.produce_queue) > 0:
      # data = kwargs['mock_generator'].get_users(kwargs['spawn_count'])
      # message_batch = Dipl_MessageBatch(data)
      
      message_batch = self.produce_queue.pop()
      producer.produce(
        topic = kwargs['topic_name'],
        key = int_to_bytes(message_batch.id),
        value = message_batch.data_json,
        callback = kwargs['on_produce'],
      )

      producer.flush()  # produce it synchronously
      kwargs['on_loop_end']()

    self.log("Producer.produce_queue is empty. Producer done.")


