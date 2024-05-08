
# timer
import time


class Dipl_Clock:

  def __init__(self):
    super()
    self.time0 = None
    self.timestamps = []

  def start(self):
    self.time0 = time.time()

  def recalculate_delta_prev(self):
    for idx, ts_object in enumerate(self.timestamps):
      if idx == 0:
        ts_object['delta_prev'] = 0
      else:
        prev_ts_object = self.timestamps[idx - 1]
        ts_object['delta_prev'] = ts_object['delta_start'] - prev_ts_object['delta_start']


  def add_custom_timestamp(self, timestamp: float, label=None):
    if not self.time0:
      raise Exception("Clock not yet initialized! Call clock.start before add_timestamp")
    elif timestamp < self.time0:
      raise Exception("Cannot add timestamp which happened before clock initialization")
    else:
      delta_start = timestamp - self.time0
      self.timestamps = [
        *[el for el in self.timestamps if el['delta_start'] <= delta_start],
        {
          '_label': label,
          'delta_start': round(delta_start, 2),
          'delta_prev': None,
        },
        *[el for el in self.timestamps if el['delta_start'] > delta_start],
      ]
      self.recalculate_delta_prev()

  def add_timestamp(self, label=None):
    curr_time = time.time()
    self.add_custom_timestamp(curr_time, label)
