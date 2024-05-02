import sys
import helpers.proj_config as proj_config
from confluent_kafka import Consumer, KafkaError, KafkaException

conf = {
  'bootstrap.servers': proj_config.bootstrap_server,
  'group.id': proj_config.string_consumer_group_id
}

consumer = Consumer(conf)


running = True

def basic_consume_loop(consumer, topics):
  try:
    consumer.subscribe(topics)
    print('Consuming started...')

    while running:
      # Wait for a message up to 5 second
      print('Polling data (5s timeout)...', end=' ')
      msg = consumer.poll(timeout=5.0)

      if msg is None:
        print('None found.')
        continue
      else:
        print('Data found.')

      if msg.error():
        if msg.error().code() == KafkaError._PARTITION_EOF:
          # End of partition event
          sys.stderr.write(
            '%% %s [%d] reached end at offset %d\n' %
            (msg.topic(), msg.partition(), msg.offset())
          )
        else:
          raise KafkaException(msg.error())
        
      else:
        # TODO: test out msg.topic()
        # Print out the message
        print('{0}={1}'.format(msg.key(), msg.value()))
  finally:
    # Close down consumer to commit final offsets.
    consumer.close()






consumer_topics = [
  proj_config.topic_name,
  # '^regex_topic_*',  # prefixing with ^ will handle it as regex
]

basic_consume_loop(consumer, consumer_topics)
