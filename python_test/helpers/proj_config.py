
import argparse


#bootstrap_server = 'localhost:9092'
#topic_name = 'diplomski_test_topic'
string_consumer_group_id = 'strings_group'
protobuf_consumer_group_id = 'protobuf_group'
default_produce_count = 10
default_spawn_count = 1000



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
  default=default_produce_count,
  help=f"Number of messages to publish by Kafka producer (default: {default_produce_count})"
)
arg_parser.add_argument(
  '--spawn-count',
  dest='spawn_count',
  type=int,
  default=default_spawn_count,
  help=f"Number of users to generate for each publish (default: {default_spawn_count})"
)

arg_parser.add_argument(
  '--bootstrap-server',
  dest='bootstrap_server',
  type=str,
  required=True,
  help='Bootstrap server which holds Kafka brokers'
)
arg_parser.add_argument(
  '--topic-name',
  dest='topic_name',
  type=str,
  required=True,
  help='Name of the topic to produce to and consume from'
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
