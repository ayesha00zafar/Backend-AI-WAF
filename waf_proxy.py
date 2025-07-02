from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
import os
import time
import hashlib
from predictor import predict_request
from logger import log_request, logs  # logs used for deletion

app = Flask(__name__)

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

try:
    redis_client = redis.Redis.from_url(redis_url)
    redis_client.ping()
    limiter = Limiter(
        get_remote_address,
        app=app,
        storage_uri=redis_url,
        default_limits=["10 per minute"]
    )
except Exception:
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["10 per minute"]
    )

@app.route('/', methods=['GET'])
def home():
    return "WAF Server is Running! Use POST /check to test queries."

@app.route('/check', methods=['POST'])
@limiter.limit("10 per minute")
def check_request():
    if not request.is_json:
        return jsonify({'status': 'error', 'message': 'No JSON provided'}), 400

    http_request = request.get_json()

    try:
        start_time = time.time()
        prediction = predict_request(http_request)
        log_request(http_request, prediction)
        elapsed = (time.time() - start_time) * 1000
        print(f"Request processed in {elapsed:.2f} ms")

        if prediction == 1:
            return jsonify({'status': 'blocked', 'message': 'Malicious request detected'})
        else:
            return jsonify({'status': 'allowed', 'message': 'Request is clean'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Internal error: {str(e)}'}), 500

@app.route('/delete_logs', methods=['POST'])
def delete_logs():
    if not request.is_json:
        return jsonify({'status': 'error', 'message': 'No JSON provided'}), 400

    data = request.get_json()
    content = data.get('content', '')

    if not content:
        return jsonify({'status': 'error', 'message': 'Missing content field'}), 400

    content_hash = hashlib.sha256(content.encode()).hexdigest()

    if logs is None:
        return jsonify({'status': 'error', 'message': 'Database not connected'}), 500

    result = logs.delete_many({'content_hash': content_hash})
    return jsonify({'status': 'success', 'deleted_count': result.deleted_count})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
