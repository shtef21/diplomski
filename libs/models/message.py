
import time
from confluent_kafka import TIMESTAMP_CREATE_TIME
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer
from confluent_kafka.serialization import SerializationContext

from ..helpers.utils import data_to_json, json_to_data, int_to_bytes, bytes_to_int
from ..helpers.mock_generator import DIPL_GENDER_FEMALE, DIPL_GENDER_MALE, Dipl_MockGenerator

from ..kafka.proto.protoc_out import user_pb2


class Dipl_Batch:
  """
    Parent class used for shared fields of JSON and proto batches.

    params:
      - self.id_bytes - batch ID
      - self.spawn_count - number of users a batch contains
      - self.generated_time - time at the moment of class creation
  """

  # Static counter
  batch_counter = 0

  def __init__(self, spawn_count):
    Dipl_JsonBatch.batch_counter += 1
    self.id = Dipl_JsonBatch.batch_counter
    self.id_bytes: bytes = int_to_bytes(self.id)
    self.spawn_count: int = spawn_count
    self.generated_time: float = time.time()



class Dipl_JsonBatch(Dipl_Batch):
  """
    Class representing a Kafka message batch.

    params:
      - self.data_json - data converted to json
  """

  def __init__(self, mock_generator: Dipl_MockGenerator, spawn_count):
    Dipl_Batch.__init__(self, spawn_count)
    self.mocked_users = mock_generator.get_users(spawn_count)

  def serialize(self) -> bytes:
    data_dict_arr = [u.__dict__ for u in self.mocked_users]
    data_json: str = data_to_json(data_dict_arr)
    return data_json.encode('utf-8')


class Dipl_ProtoBatch(Dipl_Batch):

  def __init__(self, mock_generator: Dipl_MockGenerator, spawn_count):
    Dipl_Batch.__init__(self, spawn_count)
    self.mocked_users = mock_generator.get_users(spawn_count)

  def serialize(
    self,
    serialize: ProtobufSerializer,
    sr_context: SerializationContext
  ) -> bytes:
    data_proto = user_pb2.UserList()

    for mocked_user in self.mocked_users:
      user = data_proto.users.add()
      user.id = mocked_user.id
      user.username = mocked_user.username
      user.email = mocked_user.email
      user.joined = mocked_user.joined
      user.gender = user_pb2.User.MALE if mocked_user.gender == DIPL_GENDER_MALE else DIPL_GENDER_FEMALE
      user.location = mocked_user.location
      user.birthday = mocked_user.birth_date
    
    serialized_value = serialize(data_proto, sr_context)
    return serialized_value