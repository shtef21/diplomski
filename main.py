# Install required libraries:
#   pip install confluent-kafka protobuf requests colorama tqdm matplotlib

import time
import os
from pprint import pprint

from libs.kafka.json.json_producer import Dipl_JsonProducer
from libs.kafka.json.json_consumer import Dipl_JsonConsumer
from libs.helpers.mock_generator import Dipl_MockGenerator
from libs.helpers.proj_config import ArgReader, db_tablename, default_db_path
from libs.kafka.proto.proto_consumer import Dipl_ProtoConsumer
from libs.kafka.proto.proto_producer import Dipl_ProtoProducer
from libs.helpers import db

from libs.producer_runner import run_all_tests
from libs.consumer_runner import monitor_tests
from libs.stats_runner import show_stats


ARGS = ArgReader()

print('Run configuration:')
pprint(ARGS.__dict__)


# Mocked data handling
mock_generator = Dipl_MockGenerator(
  overwrite_prev=ARGS.reset_mocks,
  show_logs=ARGS.show_logs
)

# Initialize DB if needed
if ARGS.reset_db or len(db.calculate_stats().data) == 0:
  if os.path.exists(default_db_path):
    os.remove(default_db_path)
  db.create_stats_table()
  print(f'DB initialized; table {db_tablename}')


# Start JSON producer
if ARGS.is_produce:
  j_producer = Dipl_JsonProducer(ARGS.bootstrap_server)
  p_producer = Dipl_ProtoProducer(ARGS.bootstrap_server, ARGS.schema_registry_url)
  run_all_tests(j_producer, p_producer, mock_generator)

# Start JSON consumer
elif ARGS.is_json_consumer:
  consumer = Dipl_JsonConsumer(ARGS.bootstrap_server)
  monitor_tests(consumer, ARGS.is_dry_run)

# Start PROTO consumer
elif ARGS.is_proto_consumer:
  consumer = Dipl_ProtoConsumer(ARGS.bootstrap_server)
  monitor_tests(consumer, ARGS.is_dry_run)


# Show stats
if ARGS.is_stats:
  show_stats(ARGS.stats_path)

# TODO: Use 'seaborn' for visualizing data (not matplotlib)?
