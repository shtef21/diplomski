
import time

from protobuf import addressbook_pb2
from confluent_kafka import Consumer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry.protobuf import ProtobufDeserializer

from protobuf_producer import bootstrap_server, schema_registry_url, topic
import addressbook_helpers as Pb2_Helpers


# Test out pb2
person = addressbook_pb2.Person()
person.id = 1234
# person.id = '1234'  # Raises TypeError
# person.no_such_field  # Raises AttributeError
person.name = 'John Doe'
person.email = 'jdoe@example.com'
phone = person.phones.add()
phone.number = '555-4321'
phone.type = addressbook_pb2.Person.PHONE_TYPE_HOME

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
print(person.SerializeToString())  # This is a byte string
deserialized_person = addressbook_pb2.Person()
deserialized_person.ParseFromString(person.SerializeToString())
print(deserialized_person.__str__())


def produce_callback(err, msg):
    if err is not None:
        print(f'Failed to produce Person {msg.key()}: {err}')
    else:
        print(f'User {msg.key()} successfully produced: topic={msg.topic()}, partition={msg.partition()}, offset={msg.offset()}')

def main():
    topic = 'diplomski_protobuf'
    schema_registry_url = 'http://localhost:8081'
    bootstrap_server = 'localhost:9092'
    protobuf_deserializer: addressbook_pb2.AddressBook = ProtobufDeserializer(
        message_type = addressbook_pb2.AddressBook,
        conf = {
            'use.deprecated.format': False
        }
    )

    consumer_conf = {
        'bootstrap.servers': bootstrap_server,
        'group.id': 'protobuf_group',
        'auto.offset.reset': 'earliest',
    }
    consumer = Consumer(consumer_conf)
    consumer.subscribe([topic])

    while True:
        try:
            msg = consumer.poll(1.0)
            if msg is None:
                continue

            address_book: addressbook_pb2.AddressBook = protobuf_deserializer(
                msg.value(),
                SerializationContext(topic, MessageField.VALUE)
            )
            # TODO: try if address_book_2 is the thing that causes an error
            address_book_2: Pb2_Helpers.AddressBook = protobuf_deserializer(
                msg.value(),
                SerializationContext(topic, MessageField.VALUE)
            )

            if person is not None:
                print()
                print(person)
                print('-' * 20)
                print(f'people={len(address_book_2.people)}')
                for psn in address_book_2.people:
                    print(f'\t id={psn.id} name={psn.name} email={psn.email} phones={len(psn.phones)}')
                    for ph in psn.phones:
                        print(f'\t\t type={ph.type} num={ph.number}')

        except (KeyboardInterrupt):
            break
        except Exception as error:
            print(f'Error: {error}')

    consumer.close()


if __name__ == '__main__':
    main()
