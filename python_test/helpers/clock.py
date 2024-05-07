
# timer
import time

class Dipl_Clock:

  def __init__(self):
    super()
    self.time0 = None
    self.timestamps = []

  def start(self):
    self.time0 = time.time()

  def add_timestamp(self, label=None):
    if self.time0:
      curr_time = time.time()
      prev_time = self.timestamps[-1]['delta_start'] if len(self.timestamps) > 0 else self.time0
      delta_start = curr_time - self.time0
      delta_prev = curr_time - prev_time
      self.timestamps.append({
        'label': label,
        'delta_start': delta_start,
        'delta_prev': delta_prev,
      })
    else:
      raise Exception("Clock not yet initialized! Call clock.start before add_timestamp")
