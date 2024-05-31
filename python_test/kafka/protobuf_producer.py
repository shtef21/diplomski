
import time

from protobuf import addressbook_pb2
from confluent_kafka import Producer
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer


# Test out pb2
person_test = addressbook_pb2.Person()
person_test.id = 1234
# person.id = '1234'  # Raises TypeError
# person.no_such_field  # Raises AttributeError
person_test.name = 'John Doe'
person_test.email = 'jdoe@example.com'
phone_test = person_test.phones.add()
phone_test.number = '555-4321'
phone_test.type = addressbook_pb2.Person.PHONE_TYPE_HOME

""" Useful protobuf object methods:

IsInitialized():
    checks if all the required fields have been set.
__str__():
    returns a human-readable representation of the message, particularly useful for debugging. (Usually invoked as str(message) or print message.)
CopyFrom(other_msg):
    overwrites the message with the given message’s values.
Clear():
    clears all the elements back to the empty state.

SerializeToString():
    serializes the message and returns it as a string. Note that the bytes are binary, not text; we only use the str type as a convenient container.
ParseFromString(data):
    parses a message from the given string.
"""
print(person_test.SerializeToString())  # This is a byte string
deserialized_person = addressbook_pb2.Person()
deserialized_person.ParseFromString(person_test.SerializeToString())
print(deserialized_person.__str__())


def produce_callback(err, msg):
    if err is not None:
        print(f'Failed to produce Person {msg.key()}: {err}')
    else:
        print(f'User {msg.key()} successfully produced: topic={msg.topic()}, partition={msg.partition()}, offset={msg.offset()}')


topic = 'diplomski_protobuf'
schema_registry_url = 'http://localhost:8081'
bootstrap_server = 'localhost:9092'

def main():

    # Connect to Schema Registry which monitors object types and such
    sr_conf = { 'url': schema_registry_url }
    sr_client = SchemaRegistryClient(sr_conf)

    # TODO: try if it will work again with Person and not AddressBook
    string_serializer = StringSerializer('utf8')
    protobuf_serializer = ProtobufSerializer(
        msg_type = addressbook_pb2.AddressBook,
        schema_registry_client = sr_client,
        conf = {
            'use.deprecated.format': False
        }
    )

    # TODO: figure out how to delete a topic from confluentinc broker container
    producer_conf = { 'bootstrap.servers': bootstrap_server }
    producer = Producer(producer_conf)

    print(f'Producing users on topic "{topic}". ^C to exit.')
    counter = 0

    while True:
        # Serve on_delivery callbacks from previous calls to produce()
        producer.poll(0.0)

        try:
            counter += 1
            adb = addressbook_pb2.AddressBook()
            person = adb.people.add()
            person.id = counter
            person.name = 'John Doe'
            person.email = 'jdoe@example.com'
            psn_phone = person.phones.add()
            psn_phone.number = '555-4321'
            psn_phone.type = addressbook_pb2.Person.PHONE_TYPE_HOME

            produce_value = protobuf_serializer(
                adb,
                SerializationContext(topic, MessageField.VALUE)
            )

            # # Serializing like this raises the following error on consumer:
            # #   raise SerializationError("Unknown magic byte. This message was "     
            # #   confluent_kafka.serialization.SerializationError: Unknown magic byte.
            # #   This message was not produced with a Confluent Schema Registry serializer
            # produce_value_alt = adb.SerializeToString()

            print('Produce value:')
            print(produce_value)

            producer.produce(
                topic = topic,
                key = bytes(str(person.id), 'utf-8'),
                value = produce_value,
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
