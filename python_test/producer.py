import time
from confluent_kafka import Producer
from colorama import Fore, Style, Back

from python_test.helpers import proj_config
from python_test.message import Dipl_MessageBatch


class Dipl_Producer:

  def __init__(self, mock_generator, generate_count, produce_callback, on_loop_end):
    self.is_active = False
    self.mocks = mock_generator
    self.produced_count = 0
    self.generate_count = generate_count
    self.produce_callback = produce_callback
    self.on_loop_end = on_loop_end

  
  # log function
  def log(self, *args, **kwargs):
    print(
      Back.BLUE + Fore.WHITE + 'Producer:' + Style.RESET_ALL,
      *args,
      **kwargs
    )

  def produce_callback_wrapper(self, err, msg):
    self.produced_count += 1

    if err is not None:
      self.log(f'Failed to deliver message: {msg}: {err}')
    else:
      size_kb = len(msg) / 1024
      self.log(f'Produced message {msg.key()} of size {round(size_kb, 2)}kB')

    self.produce_callback(self, err, msg)


  def run(self, config, topic_name):

    producer = Producer(config)
    self.is_active = True
    self.log("I'm up! Producing started...")

    while self.is_active:
      data = self.mocks.get_many_users(self.generate_count)
      message_batch = Dipl_MessageBatch(data)

      producer.produce(
        topic=topic_name,
        key=message_batch.key,
        value=message_batch.data_json,
        callback=self.produce_callback_wrapper,
      )
      producer.flush()  # produce it synchronously
      self.produced_count += 1
      self.on_loop_end(self)

    self.log("Producer stopped.")
