

import os
import matplotlib.pyplot as plt
import pandas as pd
import time
from pathlib import Path

from .helpers.proj_config import csv_output_dir, graphs_dir
from .models.plot_info import Dipl_PlotInfo
from .helpers import db


# Columns to aggregate
processable_columns = [
  'serialize_duration',
  'produce_duration',
  'consume_duration',
  'consumed_size_kb',
  # 'consumed_size_mb',
  'deserialize_duration',
  'total_serialization_duration',
  'throughput_mbps',
]
col_unit = {
  'serialize_duration': 'ms',
  'produce_duration': 'ms',
  'consume_duration': 'ms',
  'consumed_size_kb': 'KB',
  'consumed_size_mb': 'MB',
  'deserialize_duration': 'ms',
  'total_serialization_duration': 'ms',
  'throughput_mbps': 'mbps',
}


def process_measurements(db_path: str):
  time0 = time.time()
  msmt_list = db.get_measurements(db_path)

  df = pd.DataFrame([msmt.__dict__ for msmt in msmt_list])

  # Change measuring units (s to ms)
  df['serialize_duration'] = df['serialize_duration'] * 1000
  df['produce_duration'] = df['produce_duration'] * 1000
  df['consume_duration'] = df['consume_duration'] * 1000
  df['deserialize_duration'] = df['deserialize_duration'] * 1000

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
          # Plot a bar
          # Align PROTO left and JSON right
          bar_align = 0.4 if p_idx == 0 else -0.4
          bar = plot.bar(p.x, p.y, color=p.color, width=bar_align, align='edge')[0]

          # Show amount above bar
          bar_center = bar.get_x() + bar.get_width() / 2
          height = bar.get_height()
          bar_label = f"{height:.2f}" if height < 5 else round(height)
          font_style = { 'ha': 'center', 'va': 'bottom', 'color': p.color, 'fontweight': 'bold' }
          plot.text(x=bar_center, y=height, s=bar_label, **font_style)

    # Set plots
    _set_plot(plt_1, col_mean, f'{col_name_str} ({col_unit[col_name]}) - MEAN')
    _set_plot(plt_2, col_sum, f'{col_name_str} ({col_unit[col_name]}) - SUM')
    _set_plot(plt_3, col_var, f'{col_name_str} ({col_unit[col_name]} ^2) - VARIANCE')
    _set_plot(plt_4, col_std, f'{col_name_str} ({col_unit[col_name]}) - STD Dev.')

    graphs_dump_subdir = Path(csv_path).stem
    out_dir = f'{graphs_dir}/{graphs_dump_subdir}'
    os.makedirs(out_dir, exist_ok=True)

    output_path = f'{out_dir}/{col_idx + 1}-{col_name}.png'
    plt.savefig(output_path)
    print(f'Saved figure to {output_path}')
