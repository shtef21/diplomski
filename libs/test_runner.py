
from pprint import pprint
import matplotlib.pyplot as plt
import os
from pathlib import Path
from typing import Any, Callable

from libs.models.stats import Dipl_StatsList, Dipl_StatsRow

from .kafka.proto.proto_consumer import Dipl_ProtoConsumer
from .helpers import db
from .helpers.mock_generator import Dipl_MockGenerator
from .helpers.utils import bytes_to_int
from .helpers.proj_config import default_prod_sleep, db_tablename
from .kafka.json.json_consumer import Dipl_JsonConsumer
from .kafka.proto.proto_consumer import Dipl_ProtoConsumer
from .models.message import Dipl_JsonBatch, Dipl_BatchInfo, Dipl_ProtoBatch
from .kafka.json.json_producer import Dipl_JsonProducer
from .kafka.proto.proto_producer import Dipl_ProtoProducer


def create_test_run(
  type: str,
  mock_generator: Dipl_MockGenerator,
  reps_per_test_case: int,
  Dipl_BatchClass,
):

  # Publish 1, 50, 100 users in batch
  if type == 'small':
    for user_count in [1, 50, 100]:
      for reps in range(reps_per_test_case):
        yield Dipl_BatchClass(mock_generator, user_count)

  # Publish 500, 1000 users
  elif type == 'medium':
    for user_count in [500, 1000]:
      for reps in range(reps_per_test_case):
        yield Dipl_BatchClass(mock_generator, user_count)

  # Publish 2500, 5000, 7500, 10000 users
  elif type == 'large':
    for user_count in [2500, 5000, 7500, 10000]:
      for reps in range(reps_per_test_case):
        yield Dipl_BatchClass(mock_generator, user_count)

  # Publish 25000, 40000, 55000 users
  elif type == 'extra_large':
    for user_count in [25000, 40000, 55000]:
      for reps in range(reps_per_test_case):
        yield Dipl_BatchClass(mock_generator, user_count)



def run_all_tests(
  j_prod: Dipl_JsonProducer,
  p_prod: Dipl_ProtoProducer,
  mock_generator: Dipl_MockGenerator
):
  reps = 50

  def callback(prod: Dipl_JsonProducer | Dipl_ProtoProducer, err, msg):
    if err is not None:
      prod.log(f'Failed to deliver message: {msg}: {err}')
    else:
      size_kb = len(msg) / 1024
      # prod.log(f'Produced message {bytes_to_int(msg.key())} of size {round(size_kb, 2)}kB')

  def run_test(prod, test_size, batch_class):
    prod.produce_queue = []
    for test_case in create_test_run(test_size, mock_generator, reps, batch_class):
      prod.produce_queue.append(test_case)
    prod.log(f'Inserted {len(prod.produce_queue)} messages to producer queue.')
    prod.run(
      produce_callback=lambda err, msg: callback(prod, err, msg),
      sleep_amount=default_prod_sleep
    )

  j_prod.log('Running a small test.')
  run_test(j_prod, 'small', Dipl_JsonBatch)
  p_prod.log('Running a small test.')
  run_test(p_prod, 'small', Dipl_ProtoBatch)

  j_prod.log('Running a medium test.')
  run_test(j_prod, 'medium', Dipl_JsonBatch)
  p_prod.log('Running a medium test.')
  run_test(p_prod, 'medium', Dipl_ProtoBatch)

  j_prod.log('Running a large test.')
  run_test(j_prod, 'large', Dipl_JsonBatch)
  p_prod.log('Running a large test.')
  run_test(p_prod, 'large', Dipl_ProtoBatch)

  j_prod.log('Running an extra large test.')
  run_test(j_prod, 'extra_large', Dipl_JsonBatch)
  p_prod.log('Running an extra large test.')
  run_test(p_prod, 'extra_large', Dipl_ProtoBatch)

  print('All tests done.')


def monitor_tests(cons: Dipl_JsonConsumer | Dipl_ProtoConsumer, dry_run: bool = False):

  consumer_type = 'JSON' if type(cons) == Dipl_JsonConsumer else 'PROTO'
  print(f'Started {consumer_type} test monitoring')

  results: list[Dipl_BatchInfo] = []
  def consume_callback(msg: Dipl_BatchInfo):
    cons.log(f'Consumed msg {msg.id} of size {round(msg.size_kb, 2)}kB in {round(msg.consume_duration * 1000)}ms')
    results.append(msg)
  cons.run(
    consume_callback
  )

  if not dry_run:
    db.insert_results(results)
    cons.log(f'Inserted {len(results)} rows of {consumer_type} results.')
  else:
    cons.log(f'Dry run specified. Ignoring {len(results)} rows {consumer_type} results.')





def show_stats(stats_path: str):

  stats_list = db.calculate_stats(stats_path)
  
  if len(stats_list.data) == 0:
    print('Found 0 rows. Cannot show stats.')
    return

  # TODO: somehow display variance in durations? with opacity? with many bars?

  # Make plots
  fig, axes = plt.subplots(1, 2, figsize=(15, 7))
  fig.suptitle('JSON (blue) vs PROTO (red)')

  # Unpack plots and set grids
  plt_duration, plt_size = axes.flatten()
  plt_duration.grid()
  plt_size.grid()


  def _set_plot(
    plot,
    data: Dipl_StatsList,
    ylabel: str,
    get_val: Callable[[Dipl_StatsRow], Any]
  ):
    for idx, stats in enumerate(data):
      # Show bar
      plot.set_xlabel('Object count')
      plot.set_ylabel(ylabel)
      x_prefix = ' ' if stats.type == 'proto' else ''  # Prefix ensures separate bars

      bar = plot.bar(
        stats.user_count_str,
        get_val(stats),
        color=stats.plt_bar_color,
        width=stats.plt_bar_width,
        alpha=0.5
      )[0]
      # Add a label above bar if there's enough space
      if stats.type == 'json' or stats.type == 'proto' and stats.user_count >= 5000:
        height = bar.get_height()
        plot.text(
          bar.get_x() + bar.get_width() / 2,
          height,
          round(height),
          ha='center',
          va='bottom'
        )

  # Show plot comparing consume durations
  _set_plot(
    plt_duration,
    stats_list.data,
    'Consume duration (ms)',
    lambda stats: stats.consume_duration_avg_ms,
  )

  # Show plot comparing message sizes
  _set_plot(
    plt_size,
    stats_list.data,
    'Message size (kB)',
    lambda stats: stats.size_kb_avg
  )

  filename = Path(stats_path).stem
  output_dir = './output'
  output_path = f'{output_dir}/{filename}.png'
  os.makedirs(output_dir, exist_ok=True)

  plt.savefig(output_path)
  print(f'Saved figure to {output_path}')

  plt.show()

