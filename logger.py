from dotenv import load_dotenv
load_dotenv()
from pymongo import MongoClient
from datetime import datetime
import hashlib
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mongo_uri = os.getenv("MONGO_URI")

logs = None

if mongo_uri:
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        db = client['WAF-AI']
        logs = db['RequestLogs']
        client.server_info()
        logger.info("✅ Connected to MongoDB successfully")
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        logs = None
else:
    logger.warning("⚠️ MONGO_URI not set. Skipping MongoDB connection.")

def log_request(http_request, prediction):
    """
    Log request to MongoDB with prediction results
    Args:
        http_request: Request data dictionary
        prediction: 1 for malicious, 0 for benign
    """
    if logs is None:
        logger.warning("⚠️ Logging skipped: no MongoDB connection")
        return

    try:
        url = http_request.get('URL', '').split('?')[0]  
        method = http_request.get('Method', '')
        content = http_request.get('content', '')
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]  # Truncate for readability
        
        # Determine attack type based on prediction
        is_malicious = bool(prediction == 1)
        attack_type = 'malicious' if is_malicious else 'normal'
        status = 'blocked' if is_malicious else 'allowed'
        
        # Create comprehensive log entry
        log_entry = {
            'timestamp': datetime.utcnow(),
            'ip_address': '127.0.0.1',  # Will be updated when we get real IP
            'url': url,
            'method': method,
            'content_hash': content_hash,
            'is_malicious': is_malicious,
            'prediction': status,
            'attack_type': attack_type,
            'blocked': is_malicious,
            'label': 'Malicious' if is_malicious else 'Safe',
            'type': attack_type.capitalize(),
            'status': status.capitalize()
        }

        # Insert into MongoDB
        result = logs.insert_one(log_entry)
        logger.info(f"📝 Logged request: {url} -> {status} (ID: {result.inserted_id})")
        
        return result.inserted_id
        
    except Exception as e:
        logger.error(f"❌ Failed to log to MongoDB: {e}")
        return None


