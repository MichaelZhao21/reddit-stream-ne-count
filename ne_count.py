import os
import spacy
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, udf
from pyspark.sql.types import ArrayType, StringType
from pyspark.sql.functions import col, struct, to_json

KAFKA_SERVER = "localhost:9092"
TOPIC = "reddit"
OUT_TOPIC = "names"

# Load NLP model
nlp = spacy.load("en_core_web_sm")

def extract_named_entities(text):
    # Remove all numbers from text (prevent numbers from bubbling up as NEs)
    text = ''.join([i for i in text if not i.isdigit()])

    # Process the text
    doc = nlp(text)

    # Extract named entities
    return [ent.text for ent in doc.ents]

# Main code

# Create checkpoint directory if it doesn't exist
checkpoint_dir = "/tmp/spark-checkpoints"
os.makedirs(checkpoint_dir, exist_ok=True)

# Init spark session
spark = SparkSession.builder.appName("NamedEntityProcessor").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

# Register UDF for NER
ner_udf = udf(extract_named_entities, ArrayType(StringType()))

# Perform Named Entity Recognition
lines = spark.readStream.format("kafka").option("kafka.bootstrap.servers", KAFKA_SERVER).option("subscribe", TOPIC) \
    .option("failOnDataLoss", "false").option("startingOffsets", "earliest").load().selectExpr("CAST(value AS STRING)")
entities = lines.select(
    explode(
        ner_udf(lines.value)
    ).alias('entity')
)
entityCounts = entities.groupBy('entity').count().orderBy('count', ascending=False)

# Write output to another kafka topic
query = entityCounts.select(to_json(struct("*")).alias("value")).writeStream.format("kafka").option("kafka.bootstrap.servers", KAFKA_SERVER) \
    .option("topic", OUT_TOPIC).option("checkpointLocation", checkpoint_dir).outputMode("complete").start()

# query = entityCounts\
#         .writeStream\
#         .outputMode('complete')\
#         .format('console')\
#         .start()

query.awaitTermination()
