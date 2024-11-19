import praw
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit

SUBREDDIT = "unpopularopinion"
KAFKA_SERVER = "localhost:9092"
TOPIC = "reddit"

spark = SparkSession.builder.appName("RedditWriter").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

def save(text):
    df = spark.createDataFrame([(text,)], ["value"])
    df.selectExpr("CAST(value AS STRING)").write.format("kafka").option("kafka.bootstrap.servers", KAFKA_SERVER).option("topic", TOPIC).save()


# Main code
reddit = praw.Reddit()

for comment in reddit.subreddit(SUBREDDIT).stream.comments():
    save(comment.body)

for submission in reddit.subreddit(SUBREDDIT).stream.submissions():
    save(submission.title + " " + submission.selftext)

