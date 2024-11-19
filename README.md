## Installation

You will need to do the following:

1. Install spark and make its bin folder avaliable on the PATH
2. Download kafka and extract its content to a folder (referred to as kafka installation)
3. Create `praw.ini` with Reddit credentials (for submission, I have included this file already)
4. Install `praw` and `spacy` using `pip`

## Setup Services

Start spark (running on daemon):

```bash
# Start spark
start-master.sh
start-worker.sh spark://localhost:7077
```

Then, `cd` to the kafka installation and run each of the following in a separate terminal:

```bash
bin/zookeeper-server-start.sh config/zookeeper.properties
bin/kafka-server-start.sh config/server.properties
```

From that same directory, we will create the topics:

```bash
bin/kafka-topics.sh --create --topic reddit --bootstrap-server localhost:9092
bin/kafka-topics.sh --create --topic names --bootstrap-server localhost:9092
```

`cd` to the project directory and run the following to download the NLP model:

```bash
python -m spacy download en_core_web_sm
```

## Running App

`cd` to the project directory and run each of the following in its own terminal:

```bash
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3 stream_reddit.py
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3 ne_count.py
```

To download and start elastic search and kibana (through docker):

```bash
curl -fsSL https://elastic.co/start-local | sh
```

Create a Logstash integration on Kibana. See `elastic_template.json` for what to add to an index template. Then create a table in Kibana with the specified visualization.

Table should be:
- horizontal axis - Top 20 values of entity (ranked by last value of count)
- vertical axis - Last value of count

### Resetting State

If for some reason you need to reset the kafka topics:

```bash
# cd to kafka installation
bin/kafka-topics.sh --delete --topic reddit --bootstrap-server localhost:9092
bin/kafka-topics.sh --delete --topic names --bootstrap-server localhost:9092
```