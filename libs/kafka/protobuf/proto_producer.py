import time
from confluent_kafka import Producer
from colorama import Fore, Style, Back
from ..message import Dipl_JsonBatch

from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer

from protoc_out import user_pb2

from ...helpers.proj_config import default_prod_sleep, topic_name_proto, max_msg_size
from .user_pb2_wrapper import Dipl_UserListPb2_Wrapper


def json_batch_to_pb2(batch: Dipl_JsonBatch) -> Dipl_UserListPb2_Wrapper:
  pass


class Dipl_JsonProducer:

  def __init__(self, bootstrap_server, schema_registry_url):
    self.produce_queue: list[Dipl_JsonBatch] = []
    self.config = {
      'bootstrap.servers': bootstrap_server,
      'message.max.bytes': max_msg_size,  # 10 MB is cca 60K spawn count
    }
    sr_client = SchemaRegistryClient({ 'url': schema_registry_url })
    self.serializer = ProtobufSerializer(
      msg_type=user_pb2.UserList,
      schema_registry_client=sr_client
    )

  
  # log function
  def log(self, *args, **kwargs):
    print(
      Back.LIGHTBLUE_EX + Fore.WHITE + 'PProducer:' + Style.RESET_ALL,
      *args,
      **kwargs
    )


  def run(self, produce_callback, sleep_amount=None):

    producer = Producer(self.config)
    self.log(f'Producing {len(self.produce_queue)} messages found in produce_queue...')

    while len(self.produce_queue) > 0:
      message_batch = self.produce_queue.pop()
      producer.produce(
        topic = topic_name_proto,
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

    self.log("Done producing.")


