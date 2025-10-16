from flask import Flask, render_template, jsonify
import pymongo
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# MongoDB connection
mongo_client = pymongo.MongoClient("mongodb://mongo:27017")
db = mongo_client.iot_db
collection = db.processed_data

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/data')
def get_data():
    # Get recent data (last 100 records)
    data = list(collection.find().sort("_id", -1).limit(100))
    
    # Convert ObjectId to string for JSON serialization
    for item in data:
        item['_id'] = str(item['_id'])
    
    return jsonify(data)

@app.route('/api/stats')
def get_stats():
    total_records = collection.count_documents({})
    anomalies = collection.count_documents({"is_anomaly": True})
    
    # Get device counts
    devices = collection.aggregate([
        {"$group": {"_id": "$device_id", "count": {"$sum": 1}}}
    ])
    
    # Average temperature
    avg_temp = collection.aggregate([
        {"$match": {"temperature_celsius": {"$exists": True}}},
        {"$group": {"_id": None, "avg_temp": {"$avg": "$temperature_celsius"}}}
    ])
    avg_temp_result = list(avg_temp)
    
    return jsonify({
        "total_records": total_records,
        "anomalies": anomalies,
        "devices": list(devices),
        "avg_temperature": round(avg_temp_result[0]["avg_temp"], 2) if avg_temp_result else 0
    })

@app.route('/api/anomalies')
def get_anomalies():
    # Get only anomaly records
    anomalies = list(collection.find({"is_anomaly": True}).sort("_id", -1).limit(50))
    for item in anomalies:
        item['_id'] = str(item['_id'])
    return jsonify(anomalies)

@app.route('/api/temperature/<device_id>')
def get_device_temperature(device_id):
    # Get temperature data for specific device
    data = list(collection.find({
        "device_id": device_id,
        "temperature_celsius": {"$exists": True}
    }).sort("_id", -1).limit(20))
    
    for item in data:
        item['_id'] = str(item['_id'])
    return jsonify(data)

@app.route('/api/chart-data')
def get_chart_data():
    # Get recent temperature data for charts
    temp_data = list(collection.find({
        "temperature_celsius": {"$exists": True}
    }).sort("_id", -1).limit(30))
    
    # Prepare data for Chart.js
    chart_data = {
        "temperature": [],
        "timestamps": [],
        "devices": {},
        "anomalies": {"normal": 0, "anomaly": 0}
    }
    
    for item in temp_data:
        chart_data["temperature"].append(item["temperature_celsius"])
        chart_data["timestamps"].append(item["timestamp"])
        
        # Count by device
        device = item["device_id"]
        chart_data["devices"][device] = chart_data["devices"].get(device, 0) + 1
        
        # Count anomalies
        if item.get("is_anomaly", False):
            chart_data["anomalies"]["anomaly"] += 1
        else:
            chart_data["anomalies"]["normal"] += 1
    
    return jsonify(chart_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)