
import time
from confluent_kafka import TIMESTAMP_CREATE_TIME

from ..helpers.utils import data_to_json, json_to_data, int_to_bytes, bytes_to_int
from ..helpers.mock_generator import DIPL_GENDER_FEMALE, DIPL_GENDER_MALE, Dipl_MockGenerator

from .protobuf.protoc_out import user_pb2


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
    self.id_bytes: bytes = int_to_bytes(Dipl_JsonBatch.batch_counter)
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
    mocked_users = mock_generator.get_users(spawn_count)
    data_dict_arr = [u.__dict__ for u in mocked_users]
    self.data_json: str = data_to_json(data_dict_arr)


class Dipl_ProtoBatch(Dipl_Batch):
  def __init__(self, mock_generator: Dipl_MockGenerator, spawn_count):
    Dipl_Batch.__init__(self, spawn_count)

    self.data_proto = user_pb2.UserList()
    for mocked_user in mock_generator.get_users(spawn_count):
      user = self.data_proto.users.add()
      user.id = mocked_user.id
      user.username = mocked_user.username
      user.email = mocked_user.email
      user.joined = mocked_user.joined
      user.gender = user_pb2.User.MALE if mocked_user.gender == DIPL_GENDER_MALE else DIPL_GENDER_FEMALE
      user.location = mocked_user.location
      user.birthday = mocked_user.birth_date


class Dipl_JsonBatchInfo():

  def __init__(self, kafka_msg):
    self.id = bytes_to_int(kafka_msg.key()) if kafka_msg.key() else None
    self.size_kb = len(kafka_msg) / 1024
    self.has_measurements = False
    self.ts_received = time.time()
    self.ts_created = None
    self.consume_duration = None

    if self.id:
      self.value = 'TLDR;'
      data = json_to_data(kafka_msg.value().decode('utf-8'))
      self.user_count = len(data)
    else:
      self.value = kafka_msg.value().decode('utf-8')
      self.user_count = 0
    
    ts_type, ts_milliseconds = kafka_msg.timestamp()
    if ts_type == TIMESTAMP_CREATE_TIME:
      self.ts_created = ts_milliseconds / 1000
      self.consume_duration = self.ts_received - self.ts_created
      self.has_measurements = True
    # data = dipl_utils.parse_json_str(msg_utf8)

  def __repr__(self):
    return self.__dict__.__repr__()


