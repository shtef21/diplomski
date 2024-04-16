import sys
import proj_config
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

    while running:
      # Wait for a message up to 1 second
      msg = consumer.poll(timeout=1.0)

      if msg is None:
        continue

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
    pass






consumer_topics = [
  proj_config.topic_name,
  # '^regex_topic_*',  # prefixing with ^ will handle it as regex
]

basic_consume_loop(consumer, consumer_topics)
