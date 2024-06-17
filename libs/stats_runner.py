

import os
import matplotlib.pyplot as plt
import pandas as pd
import time
from pathlib import Path
from typing import Any, Callable

from .models.plot_info import Dipl_PlotInfo
from .models.stats import Dipl_StatsList, Dipl_StatsRow
from .helpers import db


# Columns to aggregate
processable_columns = [
  'consumed_size_kb',
  'serialize_duration',
  'produce_duration',
  'consume_duration',
  'deserialize_duration',
  'throughput_kbps'
]
col_unit = {
  'consumed_size_kb': 'kB',
  'serialize_duration': 'ms',
  'produce_duration': 'ms',
  'consume_duration': 'ms',
  'deserialize_duration': 'ms',
  'throughput_kbps': 'kbps'
}


def process_measurements(db_path: str):
  time0 = time.time()
  msmt_list = db.get_measurements(db_path)
  
  # Group by 'user_count' and 'type'
  grouped = pd.DataFrame([
    msmt.__dict__ for msmt in msmt_list
  ]).groupby(['user_count', 'type'])

  # Define aggregation functions
  agg_funcs = {col: ['mean', 'sum', 'var', 'std'] for col in processable_columns}
  agg_funcs['batch_id'] = 'count'

  # Apply aggregation
  agg_df: pd.DataFrame = grouped.agg(agg_funcs)

  # Flatten MultiIndex columns
  agg_df.columns = [f'{col[0]}_{col[1]}' if col[0] != 'batch_id' else 'instance_count' for col in agg_df.columns]

  # Reset index to turn group columns into regular columns
  agg_df.reset_index(inplace=True)
  print(agg_df)

  filename = Path(db_path).stem
  output_dir = './csv_output'
  output_path = f'{output_dir}/{filename}.csv'
  os.makedirs(output_dir, exist_ok=True)
  agg_df.to_csv(output_path)

  time_diff = time.time() - time0
  print(f'Data processed in {round(time_diff, 2)}s. Output: {output_path}')


def show_stats(csv_path: str):

  if not os.path.exists(csv_path):
    raise Exception(f'Cannot find CSV file: {csv_path}')
  
  df = pd.read_csv(csv_path)
  for col_idx, col_name in enumerate(processable_columns):
    # Fetch data from DF
    col_name_str = col_name.replace('_', ' ')
    u_counts = df['user_count'].tolist()
    types = df['type'].tolist()
    col_mean = df[f'{col_name}_mean'].tolist()
    col_sum = df[f'{col_name}_sum'].tolist()
    col_var = df[f'{col_name}_var'].tolist()
    col_std = df[f'{col_name}_std'].tolist()
    msg_count = df['instance_count'].tolist()

    # Make plots
    fig, axes = plt.subplots(2, 2, figsize=(14, 7))
    fig.suptitle('JSON (blue) vs PROTO (red)')
    
    # Unpack plots and set grids
    plt_1, plt_2, plt_3, plt_4 = axes.flatten()
    plt_1.grid()
    plt_2.grid()
    plt_3.grid()
    plt_4.grid()

    # Generic plotting function
    def _set_plot(
      plot,
      value_arr: list[float],
      ylabel: str,
    ):
      plot.set_xlabel(f'Objects in message (n={msg_count[0]})')
      plot.set_ylabel(ylabel)
      xticks = [1 + val_idx + val_idx * 0.2 for val_idx in range(len(value_arr))]
      xticks_idx = [idx for idx in range(len(xticks))]
      plot.xticks(xticks)
      plot.xticks(xticks_idx, None)
      # TODO: finish this

      for json_idx in range(0, len(value_arr), 2):
        proto_idx = json_idx + 1
        plot_data = [
          Dipl_PlotInfo(u_counts[json_idx], value_arr[json_idx], 'blue'),
          Dipl_PlotInfo(u_counts[proto_idx], value_arr[proto_idx], 'red'),
        ]

        for p_idx, p in enumerate(plot_data):
          w = 0.5 if p_idx == 0 else -0.5
          plot.bar(p.user_str, p.val, color=p.color, width=w, align='edge', clip_box=True)

    # Set plots
    _set_plot(plt_1, col_mean, f'{col_name_str} ({col_unit[col_name]}) - MEAN')
    _set_plot(plt_2, col_sum, f'{col_name_str} ({col_unit[col_name]}) - SUM')
    _set_plot(plt_3, col_var, f'{col_name_str} ({col_unit[col_name]}) - VARIANCE')
    _set_plot(plt_4, col_std, f'{col_name_str} - STD Dev.')

    filename = Path(csv_path).stem
    output_dir = './output'
    output_path = f'{output_dir}/{filename}_{col_name}.png'
    os.makedirs(output_dir, exist_ok=True)

    # plt.savefig(output_path)
    # print(f'Saved figure to {output_path}')

    # Show example figure for first column
    if col_idx == 0:
      plt.show()
