# Install required libraries:
#   pip install confluent-kafka protobuf requests colorama tqdm matplotlib pandas

import os
from pprint import pprint

from libs.kafka.json.json_producer import Dipl_JsonProducer
from libs.kafka.json.json_consumer import Dipl_JsonConsumer
from libs.helpers.mock_generator import Dipl_MockGenerator
from libs.helpers.proj_config import ArgReader, default_db_path
from libs.kafka.proto.proto_consumer import Dipl_ProtoConsumer
from libs.kafka.proto.proto_producer import Dipl_ProtoProducer
from libs.helpers import db

from libs.producer_runner import run_all_tests
from libs.consumer_runner import monitor_tests
from libs.stats_runner import process_measurements, show_stats


ARGS = ArgReader()

print('Run configuration:')
pprint(ARGS.__dict__)


# Mocked data handling
mock_generator = Dipl_MockGenerator(
  overwrite_prev=ARGS.reset_mocks,
  show_logs=ARGS.show_logs
)

# Initialize DB
db_prompt = 'Delete previous DB (Y/n)?'
if ARGS.is_produce and not input(db_prompt).lower().startswith('n'):
  if os.path.exists(default_db_path):
    print('Deleting previous DB...')
    os.remove(default_db_path)
  
  initialized = db.initialize_database()
  if initialized:
    print(f'DB initialized.')
  else:
    print('Something is wrong with the database. Exiting...')
    exit()


# Start JSON producer
if ARGS.is_produce:
  j_producer = Dipl_JsonProducer(ARGS.bootstrap_server)
  p_producer = Dipl_ProtoProducer(ARGS.bootstrap_server, ARGS.schema_registry_url)
  run_all_tests(
    j_producer,
    p_producer,
    mock_generator,
    ARGS.is_dry_run
  )

# Start JSON consumer
elif ARGS.is_json_consumer:
  consumer = Dipl_JsonConsumer(ARGS.bootstrap_server)
  monitor_tests(consumer, ARGS.is_dry_run)

# Start PROTO consumer
elif ARGS.is_proto_consumer:
  consumer = Dipl_ProtoConsumer(ARGS.bootstrap_server)
  monitor_tests(consumer, ARGS.is_dry_run)


# Make calculations on stats
if ARGS.process_stats:
  process_measurements(ARGS.db_path)

# Show stats
if ARGS.show_stats:
  show_stats(ARGS.csv_path)
