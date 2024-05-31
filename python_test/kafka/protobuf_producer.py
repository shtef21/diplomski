

from confluent_kafka import Producer
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer


def main():
    topic = 'diplomski_protobuf'
    schema_registry_url = 'http://localhost:8081'
    bootstrap_servers= 'localhost:9092'

    #
    schema_registry_conf = { 'url': schema_registry_url }
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    string_serializer = StringSerializer('utf8')
    protobuf_serializer = ProtobufSerializer(
        
    )
