
import time
from confluent_kafka import TIMESTAMP_CREATE_TIME

from libs.helpers.utils import bytes_to_int


class Dipl_ProducerMeasurement():
  pass

class Dipl_ConsumerMeasurement():

  def __init__(self, kafka_msg, type, user_count):
    self.id = bytes_to_int(kafka_msg.key()) if kafka_msg.key() else None
    self.user_count = user_count
    self.size_kb = len(kafka_msg) / 1024
    self.has_measurements = False
    self.ts_received = time.time()
    self.ts_created = None
    self.consume_duration = None
    self.type = type

    ts_type, ts_milliseconds = kafka_msg.timestamp()
    if ts_type == TIMESTAMP_CREATE_TIME:
      self.ts_created = ts_milliseconds / 1000
      self.consume_duration = self.ts_received - self.ts_created
      self.has_measurements = True

  def __repr__(self):
    return self.__dict__.__repr__()
