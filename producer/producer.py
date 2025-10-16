import json
import time
import random
from confluent_kafka import Producer
from datetime import datetime

# --- Configuration ---
KAFKA_TOPIC = "iot-data"
KAFKA_BROKER = "localhost:9092"
DEVICES = ["thermostat-01", "thermostat-02", "motion-sensor-01"]

print("Starting IoT Data Producer...")

# Initialize Kafka Producer
producer = Producer({'bootstrap.servers': KAFKA_BROKER})

# --- Data Generation Loop ---
try:
    while True:
        device_id = random.choice(DEVICES)
        data = {
            "device_id": device_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        # Generate different data based on device type
        if "thermostat" in device_id:
            # Normal temperature between 18 and 26. Spike to > 35 for anomaly.
            if random.random() < 0.1: # 10% chance of anomaly
                temp = round(random.uniform(35.0, 45.0), 2)
            else:
                temp = round(random.uniform(18.0, 26.0), 2)
            data["temperature_celsius"] = temp
            data["humidity_percent"] = round(random.uniform(30.0, 70.0), 2)

        elif "motion" in device_id:
            data["motion_detected"] = random.choice([True, False])
            data["camera_status"] = "online"

        # Send data to Kafka
        producer.produce(KAFKA_TOPIC, json.dumps(data).encode('utf-8'))
        producer.flush()
        print(f"Sent: {data}")

        # Wait for a short interval
        time.sleep(random.uniform(1, 3))

except KeyboardInterrupt:
    print("\nStopping producer...")
finally:
    producer.flush()
    print("Producer closed.")