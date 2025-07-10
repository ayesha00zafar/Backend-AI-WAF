import redis
import hashlib
import json
from config import REDIS_HOST, REDIS_PORT

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

def _hash_req(req_data):
    return hashlib.sha256(json.dumps(req_data, sort_keys=True).encode()).hexdigest()

def check_cache(req_data):
    key = _hash_req(req_data)
    result = r.get(key)
    if result:
        return result.decode()
    return None

def update_cache(req_data, action):
    key = _hash_req(req_data)
    r.set(key, action, ex=300)  # Cache for 5 minutes 