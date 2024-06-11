
from typing import Any


class Dipl_StatsList():
  def __init__(self, stats_arr: list[Any]):
    self.data: list[Dipl_StatsRow] = [Dipl_StatsRow(r) for r in stats_arr]
    self.arr_user_count = [row.user_count for row in self.data]
    self.arr_user_count_str = [row.user_count_str for row in self.data]
    self.arr_type = [row.type for row in self.data]
    self.arr_consume_duration_average = [row.consume_duration_average for row in self.data]
    self.arr_consume_duration_variance = [row.consume_duration_variance for row in self.data]
    self.arr_size_kb_avg = [row.size_kb_avg for row in self.data]

class Dipl_StatsRow():
  def __init__(self, r):
    self.user_count = r[0]
    self.user_count_str = str(r[0]).replace('0000', '0K').replace('000', 'K')
    self.type = r[1]
    self.consume_duration_average = r[2]
    self.consume_duration_variance = r[3]
    self.size_kb_avg = r[4]
