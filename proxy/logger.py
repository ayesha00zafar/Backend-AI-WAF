from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client['aiwaf']
logs = db['traffic_logs']

def log_request(req_data, action):
    logs.insert_one({
        "request": req_data,
        "action": action
    }) 