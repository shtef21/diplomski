
import time
from .helpers import utils



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

  def __init__(self, data):
    self.data = data
    self.data_json = utils.data_to_json(data)

    Dipl_MessageBatch.batch_counter += 1
    self.id = Dipl_MessageBatch.batch_counter
    self.generated_time = time.time()
