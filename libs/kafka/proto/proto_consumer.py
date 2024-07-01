import time
from confluent_kafka import Consumer, KafkaError, KafkaException, TIMESTAMP_CREATE_TIME
from colorama import Fore, Style, Back

from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry.protobuf import ProtobufDeserializer

from ...helpers.utils import bytes_to_int
from ...helpers.proj_config import consumer_group_proto, max_msg_size, topic_name_proto, topic_name_info
from ...models.measurement import Dipl_ConsumerMeasurement
from .protoc_out import user_pb2
from .user_pb2_wrapper import Dipl_UserListPb2_Wrapper


class Dipl_ProtoConsumer:

  def __init__(self, bootstrap_server):
    self.is_active = False
    self.config = {
      'bootstrap.servers': bootstrap_server,
      'group.id': consumer_group_proto,
      'message.max.bytes': max_msg_size,
    }
    self.deserialize = ProtobufDeserializer(
      message_type=user_pb2.UserList,
      conf = {
        # ProtobufSerializer: the 'use.deprecated.format' configuration property
        # must be explicitly set due to backward incompatibility with older
        # confluent-kafka-python Protobuf producers and consumers.
        # See the release notes for more details.
        'use.deprecated.format': False,
      }
    )

  
  # log function
  def log(self, *args, **kwargs):
    print(
      Back.YELLOW + Fore.WHITE + 'P_Consumer:' + Style.RESET_ALL,
      *args,
      **kwargs
    )


  def run(self, consume_callback):

    topics_to_consume = [ topic_name_proto, topic_name_info ]
    try:
      consumer = Consumer(self.config)
      consumer.subscribe(topics_to_consume)
      self.log(f"I'm up!  Listening to {topics_to_consume}. (^C to exit)")

      self.is_active = True
      poll_timeout = 1.0

      while self.is_active:
        # Await data for poll_timeout seconds
        msg = consumer.poll(timeout=poll_timeout)

        if msg is None:
          continue

        elif msg.error():
          if msg.error().code() == KafkaError._PARTITION_EOF:
            # End of partition event
            self.log(f'%{msg.topic()} [{msg.partition()}] reached end at offset {msg.offset()}\n')
          else:
            raise KafkaException(msg.error())

        else:
          if msg.topic() == topic_name_proto:
            batch_id = bytes_to_int(msg.key())
            msmt = Dipl_ConsumerMeasurement(batch_id)
            msmt.consumed_size_kb = len(msg) / 1024

            ts_type, ts_milliseconds = msg.timestamp()
            if ts_type == TIMESTAMP_CREATE_TIME:
              msmt.ts3_created = ts_milliseconds / 1000

            msmt.ts4_consumed = time.time()

            proto_msg: Dipl_UserListPb2_Wrapper = self.deserialize(
              msg.value(),
              SerializationContext(topic_name_proto, MessageField.VALUE)
            )
            # self.log(f'Fetched {len(proto_msg.users)} users.')

            msmt.ts5_deserialized = time.time()
            consume_callback(msmt)

          elif msg.topic() == topic_name_info:
            self.log(f'Received INFO message: {msg.value().decode("utf-8")}')
          else:
            self.log(f'Non-standard message received:')
            self.log(msg.value())

    except KeyboardInterrupt:
      self.log('^C')
    finally:
      # Close down consumer to commit final offsets.
      consumer.close()
      self.log("Done consuming.")
