
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

print('Protobuf byte string:')
print(' >', person_test.SerializeToString())  # This is a byte string

print('\nDeserialized person:')
deserialized_person = addressbook_pb2.Person()
deserialized_person.ParseFromString(person_test.SerializeToString())
print(str(deserialized_person))
