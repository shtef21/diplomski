
import time

from protobuf import addressbook_pb2
from protobuf import newaddressbook_pb2
from confluent_kafka import Producer
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer


def produce_callback(err, msg):
    if err is not None:
        print(f'Failed to produce Person {msg.key()}: {err}')
    else:
        print(f'User {msg.key()} successfully produced: topic={msg.topic()}, partition={msg.partition()}, offset={msg.offset()}')

topic = 'diplomski_protobuf'
new_topic = 'diplomski_protobuf_new'
schema_registry_url = 'http://localhost:8081'
bootstrap_server = 'localhost:9092'

def main():

    # Connect to Schema Registry which monitors object types and such
    sr_client = SchemaRegistryClient({ 'url': schema_registry_url })

    # protobuf_serializer = ProtobufSerializer(
    #     msg_type = addressbook_pb2.AddressBook,
    #     schema_registry_client = sr_client,
    #     conf = {
    #         'use.deprecated.format': False
    #     }
    # )
    new_protobuf_serializer = ProtobufSerializer(
        msg_type = newaddressbook_pb2.NewAddressBook,
        schema_registry_client = sr_client,
        conf = {
            'use.deprecated.format': False
        }
    )

    # TODO: figure out how to delete a topic from confluentinc broker container
    # Answer: delete it by removing the created container
    producer_conf = { 'bootstrap.servers': bootstrap_server }
    producer = Producer(producer_conf)

    print(f'Producing users on topic "{topic}". ^C to exit.')
    counter = 0

    while True:
        # Serve on_delivery callbacks from previous calls to produce()
        producer.poll(0.0)

        try:
            counter += 1
            # adb = addressbook_pb2.AddressBook()
            # person = adb.people.add()
            # person.id = counter
            # person.name = 'John Doe'
            # person.email = 'jdoe@example.com'
            # psn_phone = person.phones.add()
            # psn_phone.number = '555-4321'
            # psn_phone.type = addressbook_pb2.Person.PHONE_TYPE_HOME
            # produce_value = protobuf_serializer(
            #     adb,
            #     SerializationContext(topic, MessageField.VALUE)
            # )

            new_adb = newaddressbook_pb2.NewAddressBook()
            new_adb.id = counter
            new_person = new_adb.people.add()
            new_person.id = counter
            new_person.id = counter
            new_person.name = 'John Doe'
            new_person.email = 'jdoe@example.com'
            new_psn_phone = new_person.phones.add()
            new_psn_phone.number = '555-4321'
            new_psn_phone.type = newaddressbook_pb2.NewPerson.PHONE_TYPE_HOME
            # new_produce_value = protobuf_serializer(  #! Throws ValueError because of an improper serializer
            new_produce_value = new_protobuf_serializer(
                new_adb,
                SerializationContext(topic, MessageField.VALUE),
            )

            # # Serializing like this raises the following error on consumer:
            # #   raise SerializationError("Unknown magic byte. This message was "     
            # #   confluent_kafka.serialization.SerializationError: Unknown magic byte.
            # #   This message was not produced with a Confluent Schema Registry serializer
            # produce_value_alt = adb.SerializeToString()

            print('Produce value:')
            print(produce_value)

            # # Produce old addressbook with its serializer
            # producer.produce(
            #     topic = topic,
            #     key = bytes(str(adb.id), 'utf-8'),
            #     value = produce_value,
            #     on_delivery=produce_callback
            # )
            # Produce new addressbook with new serializer
            producer.produce(
                ###! Using old topic with new protobuf throws the following error:
                ###! confluent_kafka.schema_registry.error.SchemaRegistryError: Schema being registered is incompatible with an earlier schema for subject "diplomski_protobuf-value"
                # topic = topic,
                topic = new_topic,
                key = bytes(str(new_adb.id), 'utf-8'),
                value = new_produce_value,
                on_delivery=produce_callback
            )

            time.sleep(5.0)

        except (KeyboardInterrupt, EOFError):
            break
        except ValueError:
            print('Invalid input, discarding record...')
            continue

    print('\n Flushing records...')
    producer.flush()


if __name__ == '__main__':
    main()
