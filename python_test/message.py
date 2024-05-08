
import time
from .helpers import utils



class Dipl_MessageBatch():

  def __init__(self, data):
    self.data = data

  def set_start_timestamp(self):
    self.generated_time = time.time()

  def to_json(self):
    if not self.generated_time:
      raise Exception("Please run set_start_timestamp before to_json")
    
    return utils.data_to_json({
      'data': self.data,
      'timestamp': self.generated_time
    })

