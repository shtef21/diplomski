# Install required libraries:
#   pip install confluent-kafka protobuf requests colorama tqdm matplotlib

import time
import os

from libs.kafka.json.producer import Dipl_JsonProducer
from libs.kafka.json.consumer import Dipl_JsonConsumer
from libs.helpers.mock_generator import Dipl_MockGenerator
from libs.helpers.proj_config import ARGS
from libs.kafka.message import Dipl_JsonBatch
from libs.kafka.protobuf.proto_consumer import Dipl_ProtoConsumer
from libs.kafka.protobuf.proto_producer import Dipl_ProtoProducer
from libs.test_runner import monitor_tests, run_all_tests, show_stats


# Mocked data handling
mock_generator = Dipl_MockGenerator(
  overwrite_prev=ARGS.reset_mocks,
  show_logs=ARGS.show_logs
)

# Reset DB?
if ARGS.reset_db and os.path.exists('./sql.db'):
  os.remove('./sql.db')
  print('DB deleted.')



# Start JSON producer
if ARGS.is_produce:
  j_producer = Dipl_JsonProducer(ARGS.bootstrap_server)
  p_producer = Dipl_ProtoProducer(ARGS.bootstrap_server, ARGS.schema_registry_url)
  run_all_tests(j_producer, p_producer, mock_generator)

# Start JSON consumer
elif ARGS.is_json_consumer:
  consumer = Dipl_JsonConsumer(ARGS.bootstrap_server)
  monitor_tests(consumer)

# Start proto consumer
elif ARGS.is_proto_consumer:
  consumer = Dipl_ProtoConsumer(ARGS.bootstrap_server)
  monitor_tests(consumer)

# Show stats
elif ARGS.is_stats:
  show_stats()

# TODO: Use 'seaborn' for visualizing data (not matplotlib)?
