

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
  fig, axes = plt.subplots(2, 1, figsize=(16, 9))
  fig.suptitle('JSON (blue) vs PROTO (red)')

  # Unpack plots and set grids
  plt_size, plt_duration = axes.flatten()
  plt_size.grid()
  plt_duration.grid()


  def _set_plot(
    plot,
    data: Dipl_StatsList,
    ylabel: str,
    get_val: Callable[[Dipl_StatsRow], Any]
  ):
    for stats in data:
      # Show bar
      plot.set_xlabel('Objects in message')
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
          round(height),
          ha='center',
          va='bottom'
        )

  # Show plot comparing message sizes
  _set_plot(
    plt_size,
    stats_list.data,
    'Message size (kB)',
    lambda stats: stats.size_kb_avg
  )

  # Show plot comparing consume durations
  _set_plot(
    plt_duration,
    stats_list.data,
    'Message consume duration (ms)',
    lambda stats: stats.consume_duration_avg_ms,
  )

  filename = Path(stats_path).stem
  output_dir = './output'
  output_path = f'{output_dir}/{filename}.png'
  os.makedirs(output_dir, exist_ok=True)

  plt.savefig(output_path)
  print(f'Saved figure to {output_path}')

  plt.show()
