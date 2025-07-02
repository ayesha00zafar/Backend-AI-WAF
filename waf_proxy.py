from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time
import redis
import os
from worker import handle_request_task  

app = Flask(__name__)

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

try:
    redis_client = redis.Redis.from_url(redis_url)
    redis_client.ping()
    print("Redis connection successful")
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
    task = handle_request_task.delay(http_request)

    return jsonify({
        "status": "processing",
        "message": "Request is being analyzed asynchronously.",
        "task_id": task.id
    }), 202

@app.route('/result/<task_id>', methods=['GET'])
def get_result(task_id):
    from worker import app as celery_app
    task_result = celery_app.AsyncResult(task_id)

    if task_result.state == 'PENDING':
        return jsonify({"status": "pending", "message": "Still processing..."})
    elif task_result.state == 'SUCCESS':
        result = task_result.result
        if result == 1:
            return jsonify({'status': 'blocked', 'message': 'Malicious request detected'})
        elif result == 0:
            return jsonify({'status': 'allowed', 'message': 'Request is clean'})
        else:
            return jsonify({'status': 'error', 'message': 'Task failed'})
    else:
        return jsonify({"status": task_result.state, "message": "Unknown error"}), 500

if __name__ == '__main__':
    print("Starting WAF Server! Visit http://localhost:8080 or POST to /check")
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)




