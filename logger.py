from dotenv import load_dotenv
load_dotenv()
from pymongo import MongoClient
from datetime import datetime
import os

mongo_uri = os.getenv("MONGO_URI")

logs = None

if mongo_uri:
    try:
        client = MongoClient(mongo_uri, tls=True, serverSelectionTimeoutMS=5000)
        db = client['WAF-AI']
        logs = db['RequestLogs']
       
        client.server_info()
        print("Connected to MongoDB")
    except Exception as e:
        print("Failed to connect to MongoDB:", e)
else:
    print("MONGO_URI not set. Skipping MongoDB connection.")

def log_request(http_request, prediction):
    if logs is None:
        print("Logging skipped: no MongoDB connection")
        return

    log_entry = {
        'URL': http_request.get('URL', ''),
        'Method': http_request.get('Method', ''),
        'content': http_request.get('content', ''),
        'prediction': 'blocked' if prediction == 1 else 'allowed',
        'timestamp': datetime.utcnow()
    }

    try:
        logs.insert_one(log_entry)
        print(f"Logged request: {log_entry}")
    except Exception as e:
        print("Failed to write to MongoDB:", e)

