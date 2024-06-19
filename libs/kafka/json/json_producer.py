import time
from confluent_kafka import Producer
from colorama import Fore, Style, Back
from tqdm import tqdm
from typing import Callable, Any

from ...models.message import Dipl_JsonBatch
from ...models.measurement import Dipl_ProducerMeasurement
from ...helpers.proj_config import default_prod_sleep, topic_name_json, topic_name_info, max_msg_size


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


  def run(
    self,
    produce_callback: Callable[[Dipl_ProducerMeasurement, Any, Any], None],
    sleep_amount: float = None
  ):

    producer = Producer(self.config)
    self.log(f'Producing {len(self.produce_queue)} messages found in produce_queue...')

    # Notify consumers when producing is about to start
    for i in range(5):
      info_msg = f'Test ping. Starting producer in {5 - i} seconds...'
      producer.produce(topic=topic_name_info, value=info_msg)
      self.log(f'Produced "{info_msg}"')
      producer.flush()
      time.sleep(1.0)

    for idx in tqdm(range(len(self.produce_queue))):
      message_batch = self.produce_queue[idx]
      msmt = Dipl_ProducerMeasurement(
        message_batch.id,
        'json',
        message_batch.spawn_count
      )
      msmt.ts0_generated = time.time()
      serialized_value = message_batch.serialize()
      msmt.ts1_serialized = time.time()

      producer.produce(
        topic = topic_name_json,
        key = message_batch.id_bytes,
        value = serialized_value,
        callback = lambda err, msg: produce_callback(msmt, err, msg),
      )

      producer.flush()  # produce it synchronously
      if sleep_amount:
        if sleep_amount > 0:
          time.sleep(sleep_amount)
      else:
        time.sleep(default_prod_sleep)

    self.produce_queue = []
    self.log("Done producing.")


