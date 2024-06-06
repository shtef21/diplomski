
import argparse


#bootstrap_server = 'localhost:9092'
topic_name_json = 'diplomski_json'
topic_name_protobuf = 'diplomski_protobuf'
string_consumer_group_id = 'strings_group'
protobuf_consumer_group_id = 'protobuf_group'
default_sleep_s = 0.2
max_msg_size = 10_000_000  # 10 MB

db_filename = 'sql.db'
db_tablename = 'measurements'



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
  '--bootstrap-server',
  dest='bootstrap_server',
  type=str,
  default='localhost:9092',
  help='Bootstrap server which holds Kafka brokers (default=localhost:9092)'
)

arg_required_group = arg_parser.add_mutually_exclusive_group(required=True)
arg_required_group.add_argument(
  '--producer',
  dest='is_producer',
  action='store_true',
  help='If sent, loads up the producer'
)
arg_required_group.add_argument(
  '--consumer',
  dest='is_consumer',
  action='store_true',
  help='If sent, loads up the consumer'
)
arg_required_group.add_argument(
  '--proto-producer',
  dest='is_proto_producer',
  action='store_true',
  help='If sent, loads up proto producer'
)
arg_required_group.add_argument(
  '--proto-consumer',
  dest='is_proto_consumer',
  action='store_true',
  help='If sent, loads up proto consumer'
)
arg_required_group.add_argument(
  '--show-results',
  dest='is_show_results',
  action='store_true',
  help='If sent, triggers to only show results'
)


