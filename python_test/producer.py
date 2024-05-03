import helpers.proj_config as proj_config
from confluent_kafka import Producer


def producer_logger(err, msg):
  if err is not None:
    print(' > Failed to deliver message: {0}: {1}'.format(msg, err))
  else:
    # TODO: test out msg.topic()
    print(' > Message produced: {0}={1}'.format(msg.key(), msg.value()))


producer = Producer({
  'bootstrap.servers': proj_config.bootstrap_server
})


def _produce(read_from_prompt=False):

  msg_value = '{0} topic is live!'.format(proj_config.topic_name)
  producer.produce(
    topic=proj_config.topic_name,
    key='neki_key', #proj_config.msg_key,
    value=msg_value,
    callback=producer_logger,
  )
  producer.flush()  # Publish first message right away

