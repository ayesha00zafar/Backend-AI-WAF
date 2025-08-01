from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from pymongo import MongoClient
import os
import eventlet
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize eventlet for WebSocket support
eventlet.monkey_patch()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# MongoDB connection with error handling
try:
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    # Test the connection
    client.admin.command('ping')
    db = client['WAF-AI']
    logs = db['RequestLogs']
    logger.info("✅ MongoDB connected successfully")
except Exception as e:
    logger.error(f"❌ MongoDB connection failed: {e}")
    logger.warning("⚠️  Using mock data instead")
    logs = None

@app.route("/")
def home():
    return jsonify({"message": "WAF API Server is running", "status": "ok"})

@app.route("/ping")
def ping():
    return jsonify({"message": "pong", "status": "ok"})

@app.route("/api/logs")
def get_logs():
    try:
        if logs is None:
            # Return mock data if MongoDB is not available
            mock_logs = [
                {
                    "_id": "mock1",
                    "timestamp": "2024-01-15T10:30:00Z",
                    "ip_address": "192.168.1.100",
                    "url": "http://example.com/test",
                    "method": "GET",
                    "is_malicious": False,
                    "prediction": "allowed",
                    "attack_type": "normal",
                    "blocked": False,
                    "label": "Safe",
                    "type": "Normal",
                    "status": "Allowed"
                },
                {
                    "_id": "mock2", 
                    "timestamp": "2024-01-15T10:31:00Z",
                    "ip_address": "192.168.1.101",
                    "url": "http://example.com/script?<script>alert('xss')</script>",
                    "method": "POST",
                    "is_malicious": True,
                    "prediction": "blocked",
                    "attack_type": "malicious",
                    "blocked": True,
                    "label": "Malicious",
                    "type": "Malicious",
                    "status": "Blocked"
                }
            ]
            return jsonify({"logs": mock_logs})
        
        log_list = list(logs.find().sort('timestamp', -1).limit(100))
        for log in log_list:
            log['_id'] = str(log['_id'])
        logger.info(f"📊 Retrieved {len(log_list)} logs from MongoDB")
        return jsonify({"logs": log_list})
    except Exception as e:
        logger.error(f"Error fetching logs: {e}")
        return jsonify({"logs": [], "error": str(e)})

@app.route("/api/stats")
def get_stats():
    """
    Get WAF statistics including total, malicious, and benign requests
    """
    try:
        if logs is None:
            # Return mock stats if MongoDB is not available
            mock_stats = {
                "total_requests": 150,
                "malicious_requests": 25,
                "benign_requests": 125,
                "blocked_requests": 25,
                "allowed_requests": 125,
                "attack_types": {
                    "XSS": 10,
                    "SQL Injection": 8,
                    "Path Traversal": 5,
                    "Command Injection": 2
                },
                "recent_activity": {
                    "last_hour": 15,
                    "last_24_hours": 45,
                    "last_7_days": 150
                }
            }
            return jsonify(mock_stats)
        
        # Get real stats from MongoDB
        total_requests = logs.count_documents({})
        malicious_requests = logs.count_documents({"is_malicious": True})
        benign_requests = logs.count_documents({"is_malicious": False})
        blocked_requests = logs.count_documents({"blocked": True})
        allowed_requests = logs.count_documents({"blocked": False})
        
        # Get attack type distribution
        attack_types = {}
        attack_type_pipeline = [
            {"$match": {"is_malicious": True}},
            {"$group": {"_id": "$attack_type", "count": {"$sum": 1}}}
        ]
        attack_type_results = list(logs.aggregate(attack_type_pipeline))
        for result in attack_type_results:
            attack_types[result['_id']] = result['count']
        
        # Get recent activity
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        last_hour = logs.count_documents({"timestamp": {"$gte": now - timedelta(hours=1)}})
        last_24_hours = logs.count_documents({"timestamp": {"$gte": now - timedelta(days=1)}})
        last_7_days = logs.count_documents({"timestamp": {"$gte": now - timedelta(days=7)}})
        
        stats = {
            "total_requests": total_requests,
            "malicious_requests": malicious_requests,
            "benign_requests": benign_requests,
            "blocked_requests": blocked_requests,
            "allowed_requests": allowed_requests,
            "attack_types": attack_types,
            "recent_activity": {
                "last_hour": last_hour,
                "last_24_hours": last_24_hours,
                "last_7_days": last_7_days
            }
        }
        
        logger.info(f"📈 Stats: Total={total_requests}, Malicious={malicious_requests}, Benign={benign_requests}")
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return jsonify({
            "error": str(e),
            "total_requests": 0,
            "malicious_requests": 0,
            "benign_requests": 0,
            "blocked_requests": 0,
            "allowed_requests": 0,
            "attack_types": {},
            "recent_activity": {"last_hour": 0, "last_24_hours": 0, "last_7_days": 0}
        })

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected to SocketIO')
    socketio.emit('status', {'message': 'Connected to WAF API'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected from SocketIO')

if __name__ == "__main__":
    logger.info("🚀 Starting WAF API Server...")
    logger.info("📡 WebSocket server will be available on ws://localhost:5000")
    logger.info("🌐 HTTP API will be available on http://localhost:5000")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)