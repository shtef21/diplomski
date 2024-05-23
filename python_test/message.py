
import time
from .helpers.utils import data_to_json, bytes_to_int
from confluent_kafka import TIMESTAMP_CREATE_TIME


class Dipl_MessageBatch():
  """
    Object representing a Kafka message batch.

    params:
      - self.data - raw data sent to the constructor
      - self.data_json - data converted to json
      - self.id - integer representing batch ID
      - self.generated_time - timestamp of creation
  """

  # Static counter
  batch_counter = 0

  def __init__(self, mock_generator, spawn_count):
    data = mock_generator.get_users(spawn_count)
    self.data_json = data_to_json(data)

    Dipl_MessageBatch.batch_counter += 1
    self.id = Dipl_MessageBatch.batch_counter
    self.generated_time = time.time()




class Dipl_MessageBatchInfo():


  def __init__(self, kafka_msg):
    self.id = bytes_to_int(kafka_msg.key()) if kafka_msg.key() else None
    self.size_kb = len(kafka_msg) / 1024
    self.value = 'TLDR;' if self.id else kafka_msg.value()
    self.has_measurements = False
    self.ts_received = time.time()
    self.ts_created = None
    self.consume_duration = None
    
    ts_type, ts_milliseconds = kafka_msg.timestamp()

    if ts_type == TIMESTAMP_CREATE_TIME:
      self.ts_created = ts_milliseconds / 1000
      self.consume_duration = self.ts_received - self.ts_created
      self.has_measurements = True
    # data = dipl_utils.parse_json_str(msg_utf8)


  def __repr__(self):
    return self.__dict__.__repr__()


