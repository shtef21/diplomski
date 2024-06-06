
import argparse


topic_name_json = 'diplomski_json'
topic_name_proto = 'diplomski_protobuf'
consumer_group_json = 'strings_group'
consumer_group_protobuf = 'protobuf_group'
max_msg_size = 10_000_000  # 10 MB

default_bserver = 'localhost:9092'
default_prod_sleep = 0.5
default_sr_url = 'http://localhost:8081'

db_filename = 'sql.db'
db_tablename = 'measurements'




# Wrapper which enables linting
class ArgsWraper():
  def __init__(self):
    # Initialize parser
    arg_parser = argparse.ArgumentParser(description="Kafka communication code")

    # reset_mocks
    arg_parser.add_argument(
      '--reset-mocks',
      dest='reset_mocks',
      action='store_true',
      help='If sent, mocked data will be generated even if it already exists'
    )
    # show_logs
    arg_parser.add_argument(
      '--show-logs',
      dest='show_logs',
      action='store_true',
      help='If sent, various logs will be shown'
    )
    # bootstrap_server
    arg_parser.add_argument(
      '--bootstrap-server',
      dest='bootstrap_server',
      type=str,
      default=default_bserver,
      help=f'Bootstrap server which holds Kafka brokers (default={default_bserver})'
    )
    # schema_registry_url
    arg_parser.add_argument(
      '--schema-registry',
      dest='schema_registry_url',
      type=str,
      default=default_sr_url,
      help=f'Schema registry server (default={default_sr_url})'
    )

    arg_required_group = arg_parser.add_mutually_exclusive_group(required=True)
    # is_json_producer
    arg_required_group.add_argument(
      '--json-producer',
      dest='is_json_producer',
      action='store_true',
      help='If sent, loads up the producer'
    )
    # is_json_consumer
    arg_required_group.add_argument(
      '--json-consumer',
      dest='is_json_consumer',
      action='store_true',
      help='If sent, loads up the consumer'
    )
    # is_proto_producer
    arg_required_group.add_argument(
      '--proto-producer',
      dest='is_proto_producer',
      action='store_true',
      help='If sent, loads up proto producer'
    )
    # is_proto_consumer
    arg_required_group.add_argument(
      '--proto-consumer',
      dest='is_proto_consumer',
      action='store_true',
      help='If sent, loads up proto consumer'
    )
    # is_stats
    arg_required_group.add_argument(
      '--stats',
      dest='is_stats',
      action='store_true',
      help='If sent, only shows stats'
    )

    # Parse and save args to enable linting
    a = arg_parser.parse_args()
    self.reset_mocks = a.reset_mocks
    self.show_logs = a.show_logs
    self.bootstrap_server = a.bootstrap_server
    self.schema_registry_url = a.schema_registry_url
    self.is_json_producer = a.is_json_producer
    self.is_json_consumer = a.is_json_consumer
    self.is_proto_producer = a.is_proto_producer
    self.is_proto_consumer = a.is_proto_consumer
    self.is_stats = a.is_stats


ARGS = ArgsWraper()
