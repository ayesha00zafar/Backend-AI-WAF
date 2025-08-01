# logger.py
from pymongo import MongoClient
from datetime import datetime
import os

mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
db = client['WAF-AI']
logs = db['RequestLogs']

def log_request(http_request, prediction):
    log_entry = {
        'timestamp': datetime.utcnow(),
        'URL': http_request.get('URL', ''),
        'Method': http_request.get('Method', ''),
        'content': http_request.get('content', ''),
        'headers': http_request.get('headers', {}),
        'prediction': 'blocked' if prediction == 1 else 'allowed'
    }
    logs.insert_one(log_entry)