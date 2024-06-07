import time
from confluent_kafka import Consumer, KafkaError, KafkaException
from colorama import Fore, Style, Back

from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry.protobuf import ProtobufDeserializer

from ...helpers.proj_config import consumer_group_proto, max_msg_size, topic_name_proto
from ..message import Dipl_BatchInfo
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
      Back.LIGHTRED_EX + Fore.WHITE + 'PConsumer:' + Style.RESET_ALL,
      *args,
      **kwargs
    )


  def run(self, consume_callback):

    topics_to_consume = [ topic_name_proto ]
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
            proto_msg: Dipl_UserListPb2_Wrapper = self.deserialize(
              msg.value(),
              SerializationContext(topic_name_proto, MessageField.VALUE)
            )
            info = Dipl_BatchInfo(msg, 'proto', len(proto_msg.users))
            consume_callback(info)
          else:
            # Only happens if topics_to_consume has many topics
            self.log(f'Non-standard message received:')
            self.log(msg.value())

    except KeyboardInterrupt:
      self.log('^C')
    finally:
      # Close down consumer to commit final offsets.
      consumer.close()
      self.log("Done consuming.")
