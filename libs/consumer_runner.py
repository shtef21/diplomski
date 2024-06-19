
from .kafka.proto.proto_consumer import Dipl_ProtoConsumer
from .helpers import db
from .kafka.json.json_consumer import Dipl_JsonConsumer
from .kafka.proto.proto_consumer import Dipl_ProtoConsumer
from .models.measurement import Dipl_ConsumerMeasurement


def monitor_tests(cons: Dipl_JsonConsumer | Dipl_ProtoConsumer, dry_run: bool = False):

  consumer_type = 'JSON' if type(cons) == Dipl_JsonConsumer else 'PROTO'
  print(f'Started {consumer_type} test monitoring')

  measurements: list[Dipl_ConsumerMeasurement] = []

  def consume_callback(msmt: Dipl_ConsumerMeasurement):
    consume_dur = msmt.ts4_consumed - msmt.ts3_created
    cons.log(f'Consumed msg {msmt.batch_id} of size {round(msmt.consumed_size_kb, 2)}kB in {round(consume_dur * 1000)}ms')
    measurements.append(msmt)

  cons.run(consume_callback)

  if len(measurements) > 0:
    if not dry_run:
      db.update_consumer_msmts(measurements)
      cons.log(f'Inserted {len(measurements)} rows of {consumer_type} results.')
    else:
      cons.log(f'Dry run specified. Ignoring {len(measurements)} rows {consumer_type} results.')
