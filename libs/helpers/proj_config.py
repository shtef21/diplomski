
import argparse


topic_name_json = 'diplomski_json'    # JSON messages
topic_name_proto = 'diplomski_proto'  # PROTO messages
topic_name_info = 'dipomski_info'     # Info messages (not measured)

consumer_group_json = 'json_group'
consumer_group_proto = 'proto_group'
max_msg_size = 10_000_000  # 10 MB

default_bserver = 'localhost:9092'
default_prod_sleep = 0.5
default_sr_url = 'http://localhost:8081'

default_db_path = './sql.db'
db_tablename = 'measurements'




# Wrapper which enables linting
class ArgReader():
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
    # is_dry_run
    arg_parser.add_argument(
      '--dry-run',
      dest='is_dry_run',
      action='store_true',
      help='If sent, output results will not be saved'
    )

    arg_required_group = arg_parser.add_mutually_exclusive_group(required=True)
    # is_produce
    arg_required_group.add_argument(
      '--run-producers',
      dest='is_produce',
      action='store_true',
      help='If sent, loads up producing of JSON and PROTO messages'
    )
    # is_json_consumer
    arg_required_group.add_argument(
      '--json-consumer',
      dest='is_json_consumer',
      action='store_true',
      help='If sent, loads up the consumer'
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
    
    # stats_path
    arg_parser.add_argument(
      '--stats-path',
      dest='stats_path',
      type=str,
      default=default_db_path,
      help=f'Bootstrap server which holds Kafka brokers (default={default_db_path})'
    )

    # Parse and save args to enable linting
    a = arg_parser.parse_args()
    self.reset_mocks = a.reset_mocks
    self.show_logs = a.show_logs
    self.bootstrap_server = a.bootstrap_server
    self.stats_path = a.stats_path
    self.schema_registry_url = a.schema_registry_url
    self.is_dry_run = a.is_dry_run
    self.is_produce = a.is_produce
    self.is_json_consumer = a.is_json_consumer
    self.is_proto_consumer = a.is_proto_consumer
    self.is_stats = a.is_stats
