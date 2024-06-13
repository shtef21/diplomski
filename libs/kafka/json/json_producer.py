import time
from confluent_kafka import Producer
from colorama import Fore, Style, Back
from tqdm import tqdm

from ...models.message import Dipl_JsonBatch
from ...helpers.proj_config import default_prod_sleep, topic_name_json, max_msg_size


class Dipl_JsonProducer:

  def __init__(self, bootstrap_server):
    self.produce_queue: list[Dipl_JsonBatch] = []
    self.config = {
      'bootstrap.servers': bootstrap_server,
      'message.max.bytes': max_msg_size,  # 10 MB is cca 60K spawn count
    }

  
  # log function
  def log(self, *args, **kwargs):
    print(
      Back.BLUE + Fore.WHITE + 'J_Producer:' + Style.RESET_ALL,
      *args,
      **kwargs
    )


  def run(self, produce_callback, sleep_amount=None):

    producer = Producer(self.config)
    self.log(f'Producing {len(self.produce_queue)} messages found in produce_queue...')

    for idx in tqdm(range(len(self.produce_queue))):
      message_batch = self.produce_queue[idx]
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
        time.sleep(default_prod_sleep)

    self.produce_queue = []
    self.log("Done producing.")


