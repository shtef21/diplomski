
from typing import Any


class Dipl_StatsList():
  def __init__(self, stats_arr: list[Any]):
    self.data: list[Dipl_StatsRow] = [Dipl_StatsRow(r) for r in stats_arr]


class Dipl_StatsRow():
  def __init__(self, r):
    self.user_count = r[0]
    self.type = r[1]
    self.consume_duration_avg = r[2]
    self.consume_duration_avg_ms = r[2] * 1000
    self.consume_duration_variance = r[3]
    self.size_kb_avg = r[4]
    self.user_count_str = str(r[0]).replace('0000', '0K').replace('000', 'K')
    self.plt_bar_color = 'blue' if self.type == 'json' else 'red'
    self.plt_bar_width = 0.5 if self.type == 'json' else 0.6
