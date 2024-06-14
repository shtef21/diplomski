
from typing import Any, Callable


class Dipl_StatsRow():
  def __init__(self, r):
    # DB columns
    self.user_count = r['user_count']
    self.type = r['type']
    self.repetition_count = r['repetition_count']
    self.serialize_duration_avg = r['serialize_duration_avg']
    self.serialize_duration_sum = r['serialize_duration_sum']
    self.produce_duration_avg = r['produce_duration_avg']
    self.consume_duration_avg = r['consume_duration_avg']
    self.deserialize_duration_avg = r['deserialize_duration_avg']
    self.deserialize_duration_sum = r['deserialize_duration_sum']
    self.produced_size_kb_avg = r['produced_size_kb_avg']
    self.consumed_size_kb_avg = r['consumed_size_kb_avg']
    self.throughput_kbps_avg = r['throughput_kbps_avg']

    # Calculated columns
    self.user_count_str = str(self.user_count) \
      .replace('0000', '0K') \
      .replace('000', 'K')
    self.type = r['type']
    self.plt_bar_color = 'blue' if self.type == 'json' else 'red'
    self.plt_bar_width = 0.5 if self.type == 'json' else 0.6


class Dipl_StatsList():
  def __init__(self, query_results: list):
    self.data = [Dipl_StatsRow(row) for row in query_results]
    self.messages_per_test = 0 if len(self.data) == 0 else self.data[0].repetition_count

  def extract_column_values(self, column_name: str) -> list:
    return [row.__dict__[column_name] for row in self.data]
