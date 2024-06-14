

import matplotlib.pyplot as plt
import os
from pathlib import Path
from typing import Any, Callable

from .models.stats import Dipl_StatsList, Dipl_StatsRow
from .helpers import db



def show_stats(stats_path: str):

  stats_list = db.calculate_stats(stats_path)
  
  if len(stats_list.data) == 0:
    print('Found 0 rows. Cannot show stats.')
    return

  # TODO: somehow display variance in durations? with opacity? with many bars?

  # Make plots
  fig, axes = plt.subplots(2, 2, figsize=(15, 8))
  fig.suptitle('JSON (blue) vs PROTO (red)')

  # Unpack plots and set grids
  plt_1, plt_2, plt_3, plt_4 = axes.flatten()
  plt_1.grid()
  plt_2.grid()
  plt_3.grid()
  plt_4.grid()


  def _set_plot(
    plot,
    stats_list: Dipl_StatsList,
    ylabel: str,
    get_val: Callable[[Dipl_StatsRow], Any]
  ):
    for stats in stats_list.data:
      # Show bar
      plot.set_xlabel(f'Objects in message (n={stats_list.messages_per_test})')
      plot.set_ylabel(ylabel)

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
          f'{height:.2f}' if height < 10 else round(height),
          ha='center',
          va='bottom'
        )

  # Show plot comparing message sizes
  _set_plot(
    plt_1,
    stats_list,
    'Average message size (kB)',
    lambda stats: stats.consumed_size_kb_avg
  )

  # Show plot comparing consume durations
  _set_plot(
    plt_2,
    stats_list,
    'Average consume duration (ms)',
    lambda stats: stats.consume_duration_avg,
  )
  
  _set_plot(
    plt_3,
    stats_list,
    f'Sum serialize duration (ms), n={stats_list.messages_per_test}',
    lambda stats: stats.serialize_duration_sum,
  )
  _set_plot(
    plt_4,
    stats_list,
    f'Sum deserialize duration (ms), n={stats_list.messages_per_test}',
    lambda stats: stats.deserialize_duration_sum,
  )

  filename = Path(stats_path).stem
  output_dir = './output'
  output_path = f'{output_dir}/{filename}.png'
  os.makedirs(output_dir, exist_ok=True)

  plt.savefig(output_path)
  print(f'Saved figure to {output_path}')

  plt.show()
