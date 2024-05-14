import time
from confluent_kafka import Producer
from colorama import Fore, Style, Back

from python_test.helpers import proj_config
from python_test.message import Dipl_MessageBatch


class Dipl_Producer:

  def __init__(self, mock_generator, generate_count, produce_callback, after_callback):
    self.is_active = False
    self.mocks = mock_generator
    self.produced_count = 0
    self.generate_count = generate_count
    self.produce_callback = produce_callback
    self.after_callback = after_callback

  
  # log function
  def log(self, *args, **kwargs):
    print(
      Back.BLUE + Fore.WHITE + 'Producer:' + Style.RESET_ALL,
      *args,
      **kwargs
    )

  def on_produce_wrapper(self, err, msg):
    self.produced_count += 1
    self.produce_callback(self, err, msg)


  def run(self):

    producer = Producer({
      'bootstrap.servers': proj_config.bootstrap_server,
      'message.max.bytes': 250_086_277,
      # 'fetch.message.max.bytes': 169_086_277,
    })
    self.is_active = True
    self.log("I'm up! Producing started...")

    while self.is_active:
      data = self.mocks.get_many_users(self.generate_count)
      message_batch = Dipl_MessageBatch(data)

      producer.produce(
        topic=proj_config.topic_name,
        key=message_batch.key,
        value=message_batch.data_json,
        callback=self.on_produce_wrapper,
      )
      producer.flush()  # produce it synchronously
      self.produced_count += 1

      self.after_callback(self)

    producer.produce(
      topic=proj_config.topic_name,
      key='stop_consume',
      value=None,
      callback=self.on_produce_wrapper,
    )
    producer.flush()
