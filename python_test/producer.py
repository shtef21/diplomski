import helpers.proj_config as proj_config
from confluent_kafka import Producer

def producer_logger(err, msg):
  if err is not None:
    print(' > Failed to deliver message: {0}: {1}'.format(msg, err))
  else:
    # TODO: test out msg.topic()
    print(' > Message produced: {0}={1}'.format(msg.key(), msg.value()))



def init_producer(read_from_prompt=False):

  producer = Producer({
    'bootstrap.servers': proj_config.bootstrap_server
  })

  msg_value = '{0} topic is live!'.format(proj_config.topic_name)
  producer.produce(
    topic=proj_config.topic_name,
    key=proj_config.msg_key,
    value=proj_config.msg_value,
    callback=producer_logger,
  )
  producer.flush()  # Publish first message right away

  while read_from_prompt:
    produce_msg = input('Write message you would like to produce (or "stop" to exit): ').strip()

    if produce_msg == 'stop':
      read_from_prompt = False
    else:
      producer.produce(
        topic=proj_config.topic_name,
        key=proj_config.msg_key,
        value=produce_msg,
        callback=producer_logger,
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
      
  return producer
