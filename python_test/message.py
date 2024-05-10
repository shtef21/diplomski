
import time
from .helpers import utils



class Dipl_MessageBatch():

  # Static counter
  batch_counter = 0


  def __init__(self, data):
    self.data = data
    self.data_json = utils.data_to_json(data)
    self.set_start_timestamp()
    Dipl_MessageBatch.batch_counter += 1
    self.id = Dipl_MessageBatch.batch_counter


  def set_start_timestamp(self):
    self.generated_time = time.time()


  def entire_batch_to_json(self):
    if not self.generated_time:
      raise Exception("Please run set_start_timestamp before to_json")
    
    return utils.data_to_json({
      'id': self.id,
      'data': self.data,
      'created_timestamp': self.generated_time
    })
