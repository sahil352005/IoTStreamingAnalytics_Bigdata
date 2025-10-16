from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, when
from pyspark.sql.types import StructType, StructField, StringType, FloatType, BooleanType, TimestampType

# --- Configuration ---
KAFKA_TOPIC = "iot-data"
KAFKA_BROKER = "kafka:9092"  # Use internal Docker network name
MONGO_URI = "mongodb://mongo:27017/iot_db.processed_data"

print("Starting Spark Streaming Processor...")

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("IoTSensorAnalytics") \
    .config("spark.mongodb.output.uri", MONGO_URI) \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0,org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# --- Read from Kafka ---
kafka_stream_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "latest") \
    .load()

# Define the schema for the incoming JSON data
schema = StructType([
    StructField("device_id", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("temperature_celsius", FloatType(), True),
    StructField("humidity_percent", FloatType(), True),
    StructField("motion_detected", BooleanType(), True),
    StructField("camera_status", StringType(), True)
])

# --- Process the Data ---
# Parse the JSON string from the 'value' column
parsed_df = kafka_stream_df.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")

# Convert timestamp string to actual timestamp type
processed_df = parsed_df.withColumn("timestamp", col("timestamp").cast(TimestampType()))

# Anomaly Detection Logic
# Anomaly: Temperature > 35°C
anomaly_df = processed_df.withColumn(
    "is_anomaly",
    when(col("temperature_celsius") > 35.0, True).otherwise(False)
)

# --- Write to MongoDB ---
def write_to_mongo(df, epoch_id):
    print(f"Writing batch {epoch_id} to MongoDB...")
    if not df.rdd.isEmpty():
        df.write.format("mongo").mode("append").save()
    print(f"Batch {epoch_id} written successfully.")

query = anomaly_df.writeStream \
    .foreachBatch(write_to_mongo) \
    .outputMode("update") \
    .start()

print("Streaming query started. Waiting for termination...")
query.awaitTermination()