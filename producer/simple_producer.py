import json
import time
import random
import subprocess
from datetime import datetime

# --- Configuration ---
KAFKA_TOPIC = "iot-data"
DEVICES = ["thermostat-01", "thermostat-02", "motion-sensor-01"]

print("Starting IoT Data Producer...")

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

        # Send data to Kafka using docker exec
        json_data = json.dumps(data)
        cmd = [
            "docker", "exec", "-i", "kafka", 
            "/opt/kafka/bin/kafka-console-producer.sh",
            "--bootstrap-server", "localhost:9092",
            "--topic", KAFKA_TOPIC
        ]
        
        try:
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, text=True)
            process.communicate(input=json_data)
            print(f"Sent: {data}")
        except Exception as e:
            print(f"Error sending data: {e}")

        # Wait for a short interval
        time.sleep(random.uniform(1, 3))

except KeyboardInterrupt:
    print("\nStopping producer...")
    print("Producer closed.")