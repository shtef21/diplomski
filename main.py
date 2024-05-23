# Install required libraries:
#   pip install confluent-kafka colorama tqdm

import time

from python_test.message import Dipl_MessageBatch
from python_test.producer import Dipl_Producer
from python_test.consumer import Dipl_Consumer
from python_test.helpers.mock_generator import MockGenerator
from python_test.helpers.proj_config import arg_parser


# Setup args
received_args = arg_parser.parse_args()


# Mocked data handling
mocks = MockGenerator(
  overwrite_prev=received_args.reset_mocks,
  show_logs=received_args.show_logs,
)

if received_args.show_logs:
  mocks.show_some_data()



# Start up the producer and/or consumer
if received_args.is_producer:

  prod = Dipl_Producer()

  def on_produce(err, msg):
    if err is not None:
      prod.log(f'Failed to deliver message: {msg}: {err}')
    else:
      size_kb = len(msg) / 1024
      prod.log(f'Produced message {msg.key()} of size {round(size_kb, 2)}kB')

  def on_loop_end():
    sleep_duration = 0.5
    time.sleep(sleep_duration)

  produce_counter = received_args.produce_count

  prod.produce_queue.append(
    Dipl_MessageBatch(mocks, received_args.spawn_count)
  )
  produce_counter -= 1

  base_spawn_count = 10
  repetition_count = 1
  for multiplier in range(50, 1000, 50):
    for reps in range(repetition_count):
      prod.produce_queue.append(
        Dipl_MessageBatch(mocks, multiplier * base_spawn_count)
      )
      produce_counter -= 1

  
  
  prod.run(
    config={
      'bootstrap.servers': received_args.bootstrap_server,
      # 10 MB should be cca spawn_count=60000,
      # but max seems to be spawn_count=45000
      'message.max.bytes': 10_000_000,
    },
    topic_name=received_args.topic_name,
    on_produce = on_produce,
    on_loop_end=on_loop_end,
  )


elif received_args.is_consumer:
  print('Loading consumer...')

  def on_consumed(consumer, info):
    consumer.log(info)

  Dipl_Consumer(
    consume_callback=on_consumed,
  ).run(
    bootstrap_server=received_args.bootstrap_server,
    topic_name=received_args.topic_name,
  )


# TODO: Use 'seaborn' for visualizing data (not matplotlib)?
