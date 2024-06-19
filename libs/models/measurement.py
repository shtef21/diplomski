
class Dipl_DbMeasurement:
  """Measurement as shown in DB"""

  def __init__(self, r):
    self.batch_id = r['batch_id']
    self.type = r['type']
    self.user_count = r['user_count']
    self.produced_size_kb = r['produced_size_kb']
    self.ts0_generated = r['ts0_generated']
    self.ts1_serialized = r['ts1_serialized']
    self.ts2_produced = r['ts2_produced']
    self.ts3_created = r['ts3_created']
    self.ts4_consumed = r['ts4_consumed']
    self.ts5_deserialized = r['ts5_deserialized']
    self.consumed_size_kb = r['consumed_size_kb']
    self.serialize_duration = r['serialize_duration']
    self.produce_duration = r['produce_duration']
    self.consume_duration = r['consume_duration']
    self.deserialize_duration = r['deserialize_duration']
    self.throughput_kbps = r['throughput_kbps']


class Dipl_ProducerMeasurement():
  """Measurement used for preparing data for db in producers"""
  
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
  """Measurement used for preparing data for db in consumers"""

  def __init__(self, batch_id):
    # Set initially
    self.batch_id = batch_id
    
    # Set in consumer after fetching a message
    self.consumed_size_kb = None
    self.ts3_created = None
    self.ts4_consumed = None

    # Set in consumer after deserializing data
    self.ts5_deserialized = None

  def __repr__(self):
    return self.__dict__.__repr__()
