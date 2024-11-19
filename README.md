## Installation

You will need to do the following:

1. Install spark and make its bin folder avaliable on the PATH
2. Download kafka and extract its content to a folder (referred to as kafka installation)
3. Create `praw.ini` with Reddit credentials (for submission, I have included this file already)

## Setup Services

```
# Start spark
start-master.sh
start-worker.sh spark://localhost:7077

# cd to kafka installation
bin/zookeeper-server-start.sh config/zookeeper.properties
bin/kafka-server-start.sh config/server.properties
bin/kafka-topics.sh --create --topic reddit --bootstrap-server localhost:9092
```

## Running App

```
# From the project directory
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.1 stream_reddit.py


```