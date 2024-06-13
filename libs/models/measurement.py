
import time

class Dipl_ProducerMeasurement():
  
  def __init__(self, batch_id, type, user_count):
    # Set initially
    self.batch_id = batch_id
    self.type = type
    self.user_count = user_count

    # Set in producer after being generated
    self.ts0_generated = None

    # Set in producer after serialization (into JSON bytes or PROTO bytes)
    self.ts1_serialized = None

    # Set on produce callback
    self.ts2_produced = None
    self.produced_size_kb = None


class Dipl_ConsumerMeasurement():

  def __init__(self, batch_id):
    # Set initially
    self.batch_id = batch_id
    
    # Set in consumer after fetching a message
    self.ts3_created = None
    self.ts4_consumed = None
    self.ts5_deserialized = None
    self.consumed_size_kb = None

  def __repr__(self):
    return self.__dict__.__repr__()
