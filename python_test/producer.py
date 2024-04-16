import proj_config
from confluent_kafka import Producer

conf = {
  'bootstrap.servers': proj_config.bootstrap_server
}

producer = Producer(conf)

def some_callback(err, msg):
  if err is not None:
    print(' > Failed to deliver message: {0}: {1}'.format(msg, err))
  else:
    # TODO: test out msg.topic()
    print(' > Message produced: {0}={1}'.format(msg.key(), msg.value()))

producer.produce(
  topic=proj_config.topic_name,
  key=proj_config.msg_key,
  value=proj_config.msg_value,
  callback=some_callback,
)
producer.flush()


reading_active = True

while reading_active:
  produce_msg = input('Write message you would like to produce (or "stop" to exit): ').strip()

  if produce_msg == 'stop':
    reading_active = False
  else:
    producer.produce(
      topic=proj_config.topic_name,
      key=proj_config.msg_key,
      value=produce_msg,
      callback=some_callback,
    )
    producer.flush()


# # Wait up to 1 second for events.
# # Callbacks will be invoked during this method call
# # if the message is acknowledged
# # ------------------------------
# # From docs:
# #   poll consumes a single message,
# #   calls callbacks and returns events.
# producer.poll(1)
