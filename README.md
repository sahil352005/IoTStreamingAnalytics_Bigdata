# IoT Streaming Analytics with Kafka, Spark , MongoDB (optional InfluxDB) & Flask (Optionally Grafana)

Real-time IoT sensor data processing pipeline with anomaly detection and web dashboard visualization.



<img src="https://github.com/user-attachments/assets/b8faab88-7746-496b-9f98-158806a7418b" width="800">

<img src="https://github.com/user-attachments/assets/1edf4fb9-df83-4940-a447-795cb7009d5b" width="800">

<img src="https://github.com/user-attachments/assets/189ca213-86ec-4abc-a780-e68f229d1768" width="800">







## Architecture

```
IoT Producer → Kafka → Spark Streaming → MongoDB → Flask Dashboard
```

**Data Flow:**
1. **Producer** generates simulated IoT sensor data (temperature, humidity, motion)
2. **Kafka** streams data in real-time
3. **Spark** processes data, detects temperature anomalies (>35°C)
4. **MongoDB** stores processed results
5. **Flask Dashboard** provides real-time visualization

## Prerequisites

- Docker Desktop
- Python 3.10+
- 4GB+ RAM recommended

## Quick Start

### 1. Start Infrastructure
```bash
docker compose up -d
```

### 2. Start Spark Streaming Job
```bash
docker exec -it spark-master /opt/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0,org.mongodb.spark:mongo-spark-connector_2.12:3.0.1 /app/processor.py
```

### 3. Start Data Producer (New Terminal)
```bash
python "producer/simple_producer.py"
```

## Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| **Flask Dashboard** | `http://localhost:5000` | None |
| **MongoDB Web UI** | `http://localhost:8082` | admin/admin |
| **Spark Master UI** | `http://localhost:8081` | None |
| **InfluxDB** | `http://localhost:8086` | admin/adminpass |

## Project Structure

```
BDA project/
├── docker-compose.yml           # All services configuration
├── producer/
│   ├── simple_producer.py       # IoT data generator
│   └── requirements.txt         # Producer dependencies
├── spark_processor/
│   └── processor.py             # Spark streaming job
├── flask_dashboard/
│   ├── app.py                   # Flask web application
│   ├── requirements.txt         # Flask dependencies
│   └── templates/
│       └── dashboard.html       # Dashboard UI
├── bridge/                      # MongoDB to InfluxDB sync (optional)
└── README.md
```

## Services Overview

### Kafka & Zookeeper
- **Kafka Broker:** `localhost:9092` (external), `kafka:9092` (internal)
- **Topic:** `iot-data`
- **Auto-creates topic on startup**

### Spark Cluster
- **Master:** `localhost:8081` (Web UI), `spark://spark-master:7077` (RPC)
- **Worker:** 4 cores, 2.8GB RAM
- **Packages:** Kafka connector, MongoDB connector

### MongoDB
- **Port:** `localhost:27017`
- **Database:** `iot_db`
- **Collection:** `processed_data`
- **Web UI:** mongo-express at `localhost:8082`

### Flask Dashboard
- **Port:** `localhost:5000`
- **Features:**
  - Interactive temperature line charts (Chart.js)
  - Device distribution pie charts
  - Anomaly detection bar charts
  - Real-time statistics cards
  - Responsive Bootstrap UI
  - Color-coded data table
  - Auto-refresh every 15 seconds

## Data Schema

**Thermostat Data:**
```json
{
  "device_id": "thermostat-01",
  "timestamp": "2025-10-16T16:00:40.633871Z",
  "temperature_celsius": 21.13,
  "humidity_percent": 38.58,
  "is_anomaly": false
}
```

**Motion Sensor Data:**
```json
{
  "device_id": "motion-sensor-01",
  "timestamp": "2025-10-16T16:00:41.920381Z",
  "motion_detected": true,
  "camera_status": "online",
  "is_anomaly": false
}
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Modern dashboard with charts |
| `GET /api/data` | Recent 100 records |
| `GET /api/stats` | Statistics (total, anomalies, avg temp, device count) |
| `GET /api/anomalies` | Anomaly records only |
| `GET /api/temperature/<device_id>` | Device-specific temperature data |
| `GET /api/chart-data` | Chart data for visualizations |

## Anomaly Detection

- **Rule:** Temperature > 35°C
- **Probability:** 10% of thermostat readings are anomalies
- **Visualization:** Red highlighting in dashboard table

## Monitoring & Debugging

### Check Data Flow
```bash
# Verify Kafka has data
docker exec -it kafka /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic iot-data --from-beginning

# Check MongoDB data
docker exec -it mongo mongosh
use iot_db
db.processed_data.find().limit(5)

# View service logs
docker logs spark-master
docker logs flask-dashboard
```

### Container Status
```bash
docker ps
docker compose logs [service-name]
```

## Scaling & Performance

- **Kafka Partitions:** Currently 1, increase for higher throughput
- **Spark Workers:** Add more workers in docker-compose.yml
- **MongoDB:** Consider sharding for large datasets
- **Producer Rate:** Adjust sleep interval in producer.py

## Troubleshooting

### Common Issues

**Port Conflicts:**
- Change ports in docker-compose.yml if 8081, 5000, 8082 are in use

**Spark Job Fails:**
- Check Kafka connectivity: `docker exec -it spark-master ping kafka`
- Verify topic exists: `docker exec -it kafka /opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092`

**No Data in Dashboard:**
- Ensure producer is running and sending data
- Check Spark logs for processing errors
- Verify MongoDB connection in Flask app

**Memory Issues:**
- Reduce batch size in Spark processor
- Increase Docker memory allocation

## Stop & Cleanup

```bash
# Stop all services
docker compose down

# Remove all data (destructive)
docker compose down -v
docker system prune -f
```

## Development

### Add New Sensors
1. Modify `producer/simple_producer.py` to add device types
2. Update schema in `spark_processor/processor.py`
3. Add visualization in Flask dashboard

### Custom Anomaly Rules
Edit the anomaly detection logic in `spark_processor/processor.py`:
```python
anomaly_df = processed_df.withColumn(
    "is_anomaly",
    when(col("temperature_celsius") > 35.0, True).otherwise(False)
)
```

### Dashboard Customization
- Modify `flask_dashboard/templates/dashboard.html` for UI changes
- Add new API endpoints in `flask_dashboard/app.py`
- Customize Chart.js visualizations
- Bootstrap 5 components for responsive design
- Font Awesome icons for modern UI

## Technology Stack

- **Streaming:** Apache Kafka
- **Processing:** Apache Spark (Structured Streaming)
- **Storage:** MongoDB
- **Visualization:** Flask + Chart.js + Bootstrap 5
- **Orchestration:** Docker Compose
- **Languages:** Python, JavaScript, HTML/CSS
- **UI Framework:** Bootstrap 5, Font Awesome icons

## License

MIT License - Feel free to use and modify for your projects.
