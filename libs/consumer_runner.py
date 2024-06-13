
from .kafka.proto.proto_consumer import Dipl_ProtoConsumer
from .helpers import db
from .kafka.json.json_consumer import Dipl_JsonConsumer
from .kafka.proto.proto_consumer import Dipl_ProtoConsumer
from .models.measurement import Dipl_ConsumerMeasurement


def monitor_tests(cons: Dipl_JsonConsumer | Dipl_ProtoConsumer, dry_run: bool = False):

  consumer_type = 'JSON' if type(cons) == Dipl_JsonConsumer else 'PROTO'
  print(f'Started {consumer_type} test monitoring')

  results: list[Dipl_ConsumerMeasurement] = []
  def consume_callback(msg: Dipl_ConsumerMeasurement):
    cons.log(f'Consumed msg {msg.batch_id} of size {round(msg.consumed_size_kb, 2)}kB in {round(msg.consume_duration * 1000)}ms')
    results.append(msg)
  cons.run(
    consume_callback
  )

  if not dry_run:
    db.update_consumer_msmts(results)
    cons.log(f'Inserted {len(results)} rows of {consumer_type} results.')
  else:
    cons.log(f'Dry run specified. Ignoring {len(results)} rows {consumer_type} results.')

