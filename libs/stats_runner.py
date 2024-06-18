

import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
from pathlib import Path
from typing import Any, Callable

from .helpers.proj_config import csv_output_dir, graphs_output_dir
from .models.plot_info import Dipl_PlotInfo
from .helpers import db


# Columns to aggregate
processable_columns = [
  'consumed_size_mb',
  'serialize_duration',
  'produce_duration',
  'consume_duration',
  'deserialize_duration',
  'throughput_mbps',
  'total_serialization_duration'
]
col_unit = {
  'consumed_size_mb': 'MB',
  'serialize_duration': 'µs',
  'produce_duration': 'ms',
  'consume_duration': 'ms',
  'deserialize_duration': 'µs',
  'throughput_mbps': 'mbps',
  'total_serialization_duration': 'µs'
}


def process_measurements(db_path: str):
  time0 = time.time()
  msmt_list = db.get_measurements(db_path)

  df = pd.DataFrame([msmt.__dict__ for msmt in msmt_list])

  # Change measuring units
  df['serialize_duration'] = df['serialize_duration'] * 1000       # Millisecond to microsecond
  df['deserialize_duration'] = df['deserialize_duration'] * 1000   # Millisecond to microsecond

  # Make new columns
  df['consumed_size_mb'] = df['consumed_size_kb'] / 1024
  df['total_serialization_duration'] = df['serialize_duration'] + df['deserialize_duration']
  df['throughput_mbps'] = df['throughput_kbps'] / 1024
  
  # Group by 'user_count' and 'type'
  grouped = df.groupby(['user_count', 'type'])

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
  output_path = f'{csv_output_dir}/{filename}.csv'
  os.makedirs(csv_output_dir, exist_ok=True)

  agg_df.to_csv(output_path)
  time_diff = time.time() - time0
  print(f'Data processed in {round(time_diff, 2)}s. Output: {output_path}')


def show_stats(csv_path: str):

  if not os.path.exists(csv_path):
    raise Exception(f'Cannot find CSV file: {csv_path}')
  
  df = pd.read_csv(csv_path)
  df = df[df['user_count'] <= 10000]

  for col_idx, col_name in enumerate(processable_columns):
    # Fetch data from DF
    col_name_str = col_name.replace('_', ' ')
    u_counts = df['user_count'].tolist()
    col_mean = df[f'{col_name}_mean'].tolist()
    col_sum = df[f'{col_name}_sum'].tolist()
    col_var = df[f'{col_name}_var'].tolist()
    col_std = df[f'{col_name}_std'].tolist()
    msg_count = df['instance_count'].tolist()

    # Make plots
    fig, axes = plt.subplots(2, 2, figsize=(25, 12))
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

      def calculate_x_tick(idx):
        adjusted_idx = (idx - idx % 2) / 2
        margin = 0.05
        return round(margin + adjusted_idx + adjusted_idx * margin, 1)

      xticks = [calculate_x_tick(val_idx) for val_idx in range(len(value_arr))]
      xticks_labels = [
        str(u_counts[val_idx]).replace('0000', '0K').replace('000', 'K')
        for val_idx in range(len(value_arr))
      ]
      plot.set_xticks(xticks, xticks_labels)

      for json_idx in range(0, len(value_arr), 2):
        proto_idx = json_idx + 1
        plot_data = [
          Dipl_PlotInfo(xticks[json_idx], value_arr[json_idx], 'blue'),
          Dipl_PlotInfo(xticks[proto_idx], value_arr[proto_idx], 'red'),
        ]

        for p_idx, p in enumerate(plot_data):
          w = 0.4 if p_idx == 0 else -0.4  # Align PROTO left and JSON right
          bar = plot.bar(p.x, p.y, color=p.color, width=w, align='edge')[0]
          height = bar.get_height()
          label = f"{height:.2f}" if height < 5 else round(height)
          plot.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            label,
            ha='center',
            va='bottom',
            color=p.color,
            fontweight='bold'
          )

    # Set plots
    _set_plot(plt_1, col_mean, f'{col_name_str} ({col_unit[col_name]}) - MEAN')
    _set_plot(plt_2, col_sum, f'{col_name_str} ({col_unit[col_name]}) - SUM')
    _set_plot(plt_3, col_var, f'{col_name_str} ({col_unit[col_name]}) - VARIANCE')
    _set_plot(plt_4, col_std, f'{col_name_str} - STD Dev.')

    filename = Path(csv_path).stem
    output_path = f'{graphs_output_dir}/{filename}_{col_name}.png'
    os.makedirs(graphs_output_dir, exist_ok=True)

    plt.savefig(output_path)
    print(f'Saved figure to {output_path}')
