import time
from confluent_kafka import Producer
from colorama import Fore, Style, Back
from ..message import Dipl_JsonBatch, Dipl_ProtoBatch

from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer

from .protoc_out import user_pb2
from ...helpers.proj_config import default_prod_sleep, topic_name_proto, max_msg_size
from .user_pb2_wrapper import Dipl_UserListPb2_Wrapper


class Dipl_ProtoProducer:

  def __init__(self, bootstrap_server, schema_registry_url):
    self.produce_queue: list[Dipl_ProtoBatch] = []
    self.config = {
      'bootstrap.servers': bootstrap_server,
      # 10 MB is cca 60K spawn count
      'message.max.bytes': max_msg_size,
    }
    sr_client = SchemaRegistryClient({ 'url': schema_registry_url })
    self.serialize = ProtobufSerializer(
      msg_type=user_pb2.UserList,
      schema_registry_client=sr_client,
      conf = {
        # ProtobufSerializer: the 'use.deprecated.format' configuration property
        # must be explicitly set due to backward incompatibility with older
        # confluent-kafka-python Protobuf producers and consumers.
        # See the release notes for more details.
        'use.deprecated.format': False,
      }
    )
    self.ser_context = SerializationContext(topic_name_proto, MessageField.VALUE)

  
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
      serialized_value = self.serialize(message_batch.data_proto, self.ser_context)

      producer.produce(
        topic = topic_name_proto,
        key = message_batch.id_bytes,
        value = serialized_value,
        callback = produce_callback,
      )

      producer.flush()  # produce it synchronously
      if sleep_amount:
        if sleep_amount > 0:
          time.sleep(sleep_amount)
      else:
        time.sleep(default_prod_sleep)

    self.log("Done producing.")


