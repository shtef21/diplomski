# diplomski

Kafka + protocol buffers as an alternative to string messages

### Docs

- [GitHub repo with protocol buffers for communication](https://github.com/confluentinc/confluent-kafka-python/blob/master/examples/protobuf_producer.py)
- [Protobuf docs](https://protobuf.dev/)


# Početak rada



# Requirements (meeting held @2023-11-10)

## Problem / pitanje

- Koliko bi se mogla ubrzati komunikacija u Kafka producer-consumer okruženju
  ukoliko se poruke ne šalju preko JSONa, nego na drugačiji, serijalizirani način?
- Tu u igru dolaze protokol bufferi

## Protokol bufferi

Izvor:

- [protobuf.dev](https://protobuf.dev/)
- [protobuf sa kafkom u pythonu](https://github.com/confluentinc/confluent-kafka-python/blob/master/examples/protobuf_producer.py)

Protocol bufferi...

- sadrže strukturu objekta
- na temelju te strukture generirao bi se Kafka producer i consumer
- Kafka topic ne bi spremao podatke u JSONu i komunicirao sa stringovima
- za komunikaciju bi se koristili serijalizirani objekti

## Svrha

Postići neku vrstu Swaggera za Kafka messaging

Primjer strukture i rasporeda repozitorijâ:

1. Repo sa Protobuf objektima
2. Servis koji produca informacije
3. Servis koji consuma informacije

Automatizacija obavještavanja - čim se updejta repo sa protobuf objektima, može se svim servisima dati obavijest 'Imamo nove objekte na Kafki'.

# Testiranje

- implementirati običnu strukturu, JSONom
- implementirati protobuf strukturu

## Usporediti...

- kako se obje strukture ponašaju u komunikaciji pod raznim parametrima
- koja je optimalnija?

### Parametri...

- za, primjerice, 1000, 10000, 1 000 000 poruka?
- za velike i male poruke? kombinaciju?

### Resursi...

- Koliko se mrežnih resursa pritom potrošilo?
- Koliko je to trajalo?
- Koliko je procesorske snage potrošila serijalizacija i deserijalizacija navedenih poruka?




# Tutorial:
  - How to install Kafka using Docker & Docker Compose in any OS | Windows | MacOS | Linux | JavaTechie
  - https://www.youtube.com/watch?v=EiMi11slVnY



# Setting up Protobuf

URL for Protobuf compiler: https://protobuf.dev/downloads
To install:
- follow url to the Github release
- download suitable .zip (e.g. windows)
- unpack it and add it to PATH
- now you can use the 'protoc' compiler


# Working with Docker

## Starting zookeeper and kafka:
  - docker compose up -d
## Stopping:
  - docker compose stop

## Check if images are installed:
  - docker images

## Check process statuses:
  - docker ps


## Open kafka in terminal (it = integrated terminal, kafka = name of container image):
  - docker exec -it kafka /bin/sh
## Find kafka binary distribution:
  - ls -l opt
## Find kafka scripts (eg start kafka, create topic, produce msgs, consume msgs, ...):
  - ls -l opt/kafka_2.13-2.8.1/bin



# -------------------
#   Work with Kafka
# -------------------


## Kafka setup (from inside /opt/kafka_2.13-2.8.1)
```sh
    # ZooKeeper service
    bin/zookeeper-server-start.sh config/zookeeper.properties

    # Broker service
    bin/kafka-server-start.sh config/server.properties

    # Producer
    bin/kafka-console-producer.sh --topic SOME_TOPIC_NAME --bootstrap-server localhost:9092

    # Consumer
    bin/kafka-console-consumer.sh --topic SOME_TOPIC_NAME --from-beginning --bootstrap-server localhost:9092

    # Python Producer
    python3 main.py --run-producer --bootstrap-server localhost:9092 --topic-name SOME_TOPIC_NAME

    # Python Consumer
    python3 main.py --run-consumer --bootstrap-server localhost:9092 --topic-name SOME_TOPIC_NAME
```


## Other examples

```sh
  # Create "quickstart-events" topic
  bin/kafka-topics.sh --create --topic quickstart-events --bootstrap-server localhost:9092

  # Describe the topic
  bin/kafka-topics.sh --describe --topic quickstart-events --bootstrap-server localhost:9092

  # Then write some events with producer
  # Then read those events with consumer

  # Delete a topic
  bin/kafka-topics.sh --delete --topic quickstart-events --bootstrap-server localhost:9092
```


Open bin:
  - cd /opt/kafka_2.13-2.8.1/bin

Create topic:
  - kafka-topics.sh --create --zookeeper zookeeper:2181 --replication-factor 1 --partitions 1 --topic quickstart
Explanation:
  - kafka-topics.sh
      start topics script
  - --create
      create topic flag 
  - --zookeeper zookeeper:2181
      specify ZooKeeper connection string, which Kafka uses for maintaining config info & providing distributed sync 
  - --replication-factor 1
      replication factor is number of copies of each message stored in the cluster 
  - --partitions 1
      partitions allow a topic to be parallelized by splitting the data in a topic across multiple brokers 
  - --topic quickstart 
      specify name of the topic to be "quickstart"


Consume all messages from topic "some_topic":
  - kafka-console-consumer.sh --topic some_topic --from-beginning --bootstrap-server localhost:9092
Explanation:
  - --topic some_topic
      definition of topic name
  - --from-beginning
      read data from start of topic, and not just when consumer started
  - --bootstrap-server localhost:9092
      Specify address of the Kafka server from which consumer will consume messages

