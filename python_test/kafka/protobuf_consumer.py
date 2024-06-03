
import time

from protobuf import addressbook_pb2
from confluent_kafka import Consumer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry.protobuf import ProtobufDeserializer

from protobuf_producer import bootstrap_server, topic
import addressbook_helpers as Pb2_Helpers


def produce_callback(err, msg):
    if err is not None:
        print(f'Failed to produce Person {msg.key()}: {err}')
    else:
        print(f'User {msg.key()} successfully produced: topic={msg.topic()}, partition={msg.partition()}, offset={msg.offset()}')

def main():
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

            #address_book: addressbook_pb2.AddressBook = protobuf_deserializer(...)

            # Convert directly from protobuf's default AddressBook to a helper class
            address_book: Pb2_Helpers.AddressBookWrapper = protobuf_deserializer(
                msg.value(),
                SerializationContext(topic, MessageField.VALUE)
            )

            if address_book is not None:
                print('-' * 20)
                print(f'people={len(address_book.people)}')
                for person in address_book.people:
                    print(f'  id={person.id} name={person.name} email={person.email} phones={len(person.phones)}')
                    for phone in person.phones:
                        print(f'    type={phone.type} num={phone.number}')

        except (KeyboardInterrupt):
            break
        except Exception as error:
            print(f'Error: {error}')

    consumer.close()


if __name__ == '__main__':
    main()
