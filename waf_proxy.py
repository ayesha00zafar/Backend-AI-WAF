from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify
from predictor import predict_request
from logger import log_request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time
import redis
import os

app = Flask(__name__)

# Try connecting to Redis
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
except Exception as e:
    print(f"Redis connection failed: {e}")
    print("Using in-memory rate limiting instead (not persistent)")
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["10 per minute"]
    )

@app.route('/', methods=['GET'])
def home():
    return "WAF Server is Running! Use POST /check to test queries."

@app.route('/check', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def check_request():
    if request.method == 'GET':
        return jsonify({
            "message": "This endpoint expects POST requests with JSON payloads.",
            "usage": {
                "method": "POST",
                "url": "/check",
                "body_format": {"payload": "your_input_here"}
            }
        })

    start_time = time.time()

    if request.is_json:
        http_request = request.get_json()
        try:
            prediction = predict_request(http_request)
            log_request(http_request, prediction)
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Internal prediction error: {str(e)}"
            }), 500

        elapsed = (time.time() - start_time) * 1000
        print(f"Request processed in {elapsed:.2f} ms")

        if prediction == 1:
            return jsonify({
                'status': 'blocked',
                'message': 'Malicious request detected'
            })
        else:
            return jsonify({
                'status': 'allowed',
                'message': 'Request is clean'
            })
    else:
        return jsonify({
            'status': 'error',
            'message': 'No JSON provided'
        }), 400

if __name__ == '__main__':
    print("Starting WAF Server! Visit http://localhost:8080 or POST to /check")
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)




