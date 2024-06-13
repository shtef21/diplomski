import time
from confluent_kafka import Producer
from colorama import Fore, Style, Back
from tqdm import tqdm
from typing import Callable, Any

from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer


from ...helpers.proj_config import default_prod_sleep, topic_name_proto, max_msg_size
from ...models.message import Dipl_JsonBatch, Dipl_ProtoBatch
from ...models.measurement import Dipl_ProducerMeasurement

from .protoc_out import user_pb2


class Dipl_ProtoProducer:

  def __init__(self, bootstrap_server, schema_registry_url):
    self.produce_queue: list[Dipl_ProtoBatch] = []
    self.config = {
      'bootstrap.servers': bootstrap_server,
      # 10 MB is cca 60K spawn count
      'message.max.bytes': max_msg_size,
    }
    sr_client = SchemaRegistryClient({ 'url': schema_registry_url })
    self.serializer = ProtobufSerializer(
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
    self.sr_context = SerializationContext(topic_name_proto, MessageField.VALUE)

  
  # log function
  def log(self, *args, **kwargs):
    print(
      Back.GREEN + Fore.WHITE + 'P_Producer:' + Style.RESET_ALL,
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

    for idx in tqdm(range(len(self.produce_queue))):
      message_batch = self.produce_queue[idx]
      msmt = Dipl_ProducerMeasurement(
        message_batch.id,
        'proto',
        message_batch.spawn_count
      )
      msmt.ts0_generated = time.time()
      serialized_value = message_batch.serialize(self.serializer, self.sr_context)
      msmt.ts1_serialized = time.time()

      producer.produce(
        topic = topic_name_proto,
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


