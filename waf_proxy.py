from flask import Flask, request, jsonify
from predictor import predict_request
from logger import log_request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time
import redis
import os

redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))


app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri=os.getenv("REDIS_URL"),
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
        prediction = predict_request(http_request)
        log_request(http_request, prediction)

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
        })

if __name__ == '__main__':
    print("WAF Server is Running! Use POST /check to test queries.")
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


