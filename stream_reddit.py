import praw
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit

SUBREDDIT = "leagueoflegends"
KAFKA_SERVER = "localhost:9092"
TOPIC = "reddit"

def save(text):
    df = spark.createDataFrame([(text,)], ["value"])
    df.selectExpr("CAST(value AS STRING)").write.format("kafka").option("kafka.bootstrap.servers", KAFKA_SERVER).option("topic", TOPIC).save()


# Main code

# Init spark session
spark = SparkSession.builder.appName("RedditWriter").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

# Get reddit stream
reddit = praw.Reddit()

# Write comments and submissions to Kafka
for comment in reddit.subreddit(SUBREDDIT).stream.comments():
    save(comment.body)

for submission in reddit.subreddit(SUBREDDIT).stream.submissions():
    save(submission.title + " " + submission.selftext)

