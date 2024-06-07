# Install required libraries:
#   pip install confluent-kafka protobuf requests colorama tqdm matplotlib

import time

from libs.kafka.json.producer import Dipl_JsonProducer
from libs.kafka.json.consumer import Dipl_JsonConsumer
from libs.helpers.mock_generator import Dipl_MockGenerator
from libs.helpers.proj_config import ARGS
from libs.kafka.message import Dipl_JsonBatch
from libs.kafka.protobuf.proto_producer import Dipl_ProtoProducer
from libs.test_runner import monitor_json_tests, run_json_tests, run_proto_tests, show_stats


# Mocked data handling
mock_generator = Dipl_MockGenerator(
  overwrite_prev=ARGS.reset_mocks,
  show_logs=ARGS.show_logs
)


# Start JSON producer
if ARGS.is_json_producer:
  producer = Dipl_JsonProducer(ARGS.bootstrap_server)
  run_json_tests(producer, mock_generator)

# Start JSON consumer
elif ARGS.is_json_consumer:
  consumer = Dipl_JsonConsumer(ARGS.bootstrap_server)
  monitor_json_tests(consumer)

# Start proto producer
elif ARGS.is_proto_producer:
  producer = Dipl_ProtoProducer(ARGS.bootstrap_server, ARGS.schema_registry_url)
  run_proto_tests(producer, mock_generator)

# Start proto consumer
elif ARGS.is_proto_consumer:
  pass

# Show stats
elif ARGS.is_stats:
  show_stats()

# TODO: Use 'seaborn' for visualizing data (not matplotlib)?
