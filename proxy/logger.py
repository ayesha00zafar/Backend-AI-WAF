import logging
from datetime import datetime
from pymongo import MongoClient
from config import MONGO_URI, LOG_FILE_PATH, LOG_LEVEL, LOG_FORMAT

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client['aiwaf']
logs = db['traffic_logs']

# File logging setup
file_logger = logging.getLogger('waf_file_logger')
file_logger.setLevel(getattr(logging, LOG_LEVEL))

# Create file handler
file_handler = logging.FileHandler(LOG_FILE_PATH)
file_handler.setLevel(getattr(logging, LOG_LEVEL))

# Create formatter
formatter = logging.Formatter(LOG_FORMAT)
file_handler.setFormatter(formatter)

# Add handler to logger
file_logger.addHandler(file_handler)

def log_request(req_data, action, reason=None):
    """
    Log request to both MongoDB and file with detailed information.
    
    Args:
        req_data: Dictionary containing request data (url, ip, headers, body)
        action: 'allow' or 'block'
        reason: Reason for blocking (only for blocked requests)
    """
    timestamp = datetime.now().isoformat()
    url = req_data.get("url", "")
    ip = req_data.get("ip", "")
    
    # MongoDB logging (structured data)
    mongo_log = {
        "timestamp": timestamp,
        "request": req_data,
        "action": action,
        "url": url,
        "ip": ip
    }
    if reason:
        mongo_log["reason"] = reason
    
    logs.insert_one(mongo_log)
    
    # File logging (human-readable format)
    log_message = f"Action: {action.upper()} | URL: {url} | IP: {ip}"
    if reason:
        log_message += f" | Reason: {reason}"
    
    if action == "block":
        file_logger.warning(log_message)
    else:
        file_logger.info(log_message)

def log_block(reason, req_data):
    """
    Convenience function to log blocked requests.
    """
    log_request(req_data, "block", reason)

def log_allow(req_data):
    """
    Convenience function to log allowed requests.
    """
    log_request(req_data, "allow") 