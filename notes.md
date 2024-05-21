
# Tutorial:
  - How to install Kafka using Docker & Docker Compose in any OS | Windows | MacOS | Linux | JavaTechie
  - https://www.youtube.com/watch?v=EiMi11slVnY



# Starting zookeeper and kafka:
  - docker compose up -d
# Stopping:
  - docker compose stop

# Check if images are installed:
  - docker images

# Check process statuses:
  - docker ps


# Open kafka in terminal (it = integrated terminal):
  - docker exec -it kafka /bin/sh
# Find kafka binary distribution:
  - ls -l opt
# Find kafka scripts (eg start kafka, create topic, produce msgs, consume msgs, ...):
  - ls -l opt/kafka_2.13-2.8.1/bin



# -------------------
#   Work with Kafka
# -------------------


# Kafka setup (from inside /opt/kafka_2.13-2.8.1)
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




# Other examples

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
