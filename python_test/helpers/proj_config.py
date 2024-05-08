
import argparse



bootstrap_server = 'localhost:9092'

topic_name = 'diplomski_test_topic'
string_consumer_group_id = 'strings_group'
protobuf_consumer_group_id = 'protobuf_group'




# Command line handling
arg_parser = argparse.ArgumentParser(description="Kafka communication code")
arg_parser.add_argument(
  '--reset-mocks',
  dest='reset_mocks',
  action='store_true',
  help='If sent, mocked data will be generated even if it already exists'
)
arg_parser.add_argument(
  '--show-logs',
  dest='show_logs',
  action='store_true',
  help='If sent, various logs will be shown'
)
arg_parser.add_argument(
  '--produce-count',
  dest='produce_count',
  type=int,
  default=10,
  help="Number of messages to publish by Kafka producer (default: 10)"
)

arg_required_group = arg_parser.add_mutually_exclusive_group(required=True)
arg_required_group.add_argument(
  '--run-producer',
  dest='is_producer',
  action='store_true',
  help='If sent, loads up the producer'
)
arg_required_group.add_argument(
  '--run-consumer',
  dest='is_consumer',
  action='store_true',
  help='If sent, loads up the consumer'
)
