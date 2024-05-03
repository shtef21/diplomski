# pip install confluent-kafka

from confluent_kafka import Consumer, Producer
from colorama import Fore, Style, Back
import asyncio
import argparse

import python_test.helpers.utils as dipl_utils
from python_test.helpers.mock_generator import MockGenerator
from python_test.helpers import proj_config


# Command line handling
arg_parser = argparse.ArgumentParser(description="Kafka communication code")
arg_parser.add_argument(
  '--reset-mocks',
  dest='reset_mocks',
  action='store_true',
  help='If sent, mocked data will be generated even if it already exists'
)
arg_parser.add_argument(
  '--producer-only',
  dest='producer_only',
  action='store_true',
  help='If sent, only loads up the producer'
)
arg_parser.add_argument(
  '--consumer-only',
  dest='consumer_only',
  action='store_true',
  help='If sent, only loads up the consumer'
)
received_args = arg_parser.parse_args()


# Mocked data handling
mocks = MockGenerator(
  overwrite_prev=received_args.reset_mocks,
  show_logs=True
)
mocks.show_some_data()


# Consumer handling
async def run_consumer():
  def log(*args, **kwargs):
    print(
      Back.RED + Fore.WHITE + 'Consumer:' + Style.RESET_ALL,
      *args,
      **kwargs
    )

  topics_to_consumer = [ proj_config.topic_name ]
  try:
    consumer = Consumer({
      'bootstrap.servers': proj_config.bootstrap_server,
      'group.id': proj_config.string_consumer_group_id
    })
    log(f"I'm up!  Listening to {topics_to_consumer}...")
    
  finally:
    # Close down consumer to commit final offsets.
    consumer.close()



# Producer handling
async def run_producer():
  def log(*args, **kwargs):
    print(
      Back.BLUE + Fore.WHITE + 'Producer:' + Style.RESET_ALL,
      *args,
      **kwargs
    )

  log("I'm up! Producing started...")






# Start up the producer and/or consumer

if received_args.consumer_only:
  print('Loading consumer...')
  asyncio.run(run_consumer())

elif received_args.producer_only:
  print('Loading producer...')
  asyncio.run(run_producer())

else:
  print('Loading consumer...')
  asyncio.run(run_consumer())
  print('Loading producer...')
  asyncio.run(run_producer())


# TODO: Use 'seaborn' for visualizing data (not matplotlib)?
