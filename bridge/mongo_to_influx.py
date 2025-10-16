import time
import pymongo
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Configuration
MONGO_URI = "mongodb://mongo:27017"
INFLUX_URL = "http://influxdb:8086"
INFLUX_TOKEN = "my-super-secret-auth-token"
INFLUX_ORG = "iot-org"
INFLUX_BUCKET = "iot-data"

print("Starting MongoDB to InfluxDB bridge...")

# Connect to MongoDB
mongo_client = pymongo.MongoClient(MONGO_URI)
db = mongo_client.iot_db
collection = db.processed_data

# Connect to InfluxDB
influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

processed_ids = set()

while True:
    try:
        # Get new documents from MongoDB
        cursor = collection.find({"_id": {"$nin": list(processed_ids)}})
        
        for doc in cursor:
            # Create InfluxDB point
            point = Point("iot_sensors").tag("device_id", doc.get("device_id", "unknown"))
            
            if "temperature_celsius" in doc:
                point = point.field("temperature", float(doc["temperature_celsius"]))
            if "humidity_percent" in doc:
                point = point.field("humidity", float(doc["humidity_percent"]))
            if "motion_detected" in doc:
                point = point.field("motion", bool(doc["motion_detected"]))
            if "is_anomaly" in doc:
                point = point.field("anomaly", bool(doc["is_anomaly"]))
            
            # Write to InfluxDB
            write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
            processed_ids.add(doc["_id"])
            print(f"Synced document: {doc['device_id']}")
        
        time.sleep(5)  # Check every 5 seconds
        
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(10)