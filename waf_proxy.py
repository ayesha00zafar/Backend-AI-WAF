from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, send_file, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO, emit
import redis
import os
import time
import hashlib
import io
import csv
from predictor import predict_request
from logger import log_request, logs  # logs used for deletion

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

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
        # TODO: Integrate antivirus scanning here (before AI prediction)
        start_time = time.time()
        prediction = predict_request(http_request)
        # TODO: Integrate antivirus scanning here (after AI prediction)
        log_request(http_request, prediction)
        elapsed = (time.time() - start_time) * 1000
        print(f"Request processed in {elapsed:.2f} ms")

        # Emit real-time log update
        if logs is not None:
            last_log = logs.find().sort([('_id', -1)]).limit(1)
            for log in last_log:
                socketio.emit('new_log', {
                    'URL': log.get('URL', ''),
                    'Method': log.get('Method', ''),
                    'prediction': log.get('prediction', ''),
                    'timestamp': log.get('timestamp', '').isoformat() if log.get('timestamp') else '',
                })

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

# --- NEW ENDPOINTS FOR LOGS ---
@app.route('/api/logs', methods=['GET'])
def get_logs():
    if logs is None:
        return jsonify({'status': 'error', 'message': 'Database not connected'}), 500
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        skip = (page - 1) * per_page
        cursor = logs.find().sort([('timestamp', -1)]).skip(skip).limit(per_page)
        log_list = []
        for log in cursor:
            log_list.append({
                'id': str(log.get('_id', '')),
                'timestamp': log.get('timestamp', '').isoformat() if log.get('timestamp') else '',
                'ipAddress': '',  # Add if available
                'url': log.get('URL', ''),
                'method': log.get('Method', ''),
                'label': 'Malicious' if log.get('prediction') == 'blocked' else 'Safe',
                'type': 'Unknown',  # Add if available
                'status': 'Blocked' if log.get('prediction') == 'blocked' else 'Allowed',
            })
        total = logs.count_documents({})
        return jsonify({'logs': log_list, 'total': total})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/logs', methods=['DELETE'])
def clear_logs():
    if logs is None:
        return jsonify({'status': 'error', 'message': 'Database not connected'}), 500
    try:
        result = logs.delete_many({})
        socketio.emit('logs_cleared', {'message': 'All logs cleared'})
        return jsonify({'status': 'success', 'deleted_count': result.deleted_count})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/logs/export', methods=['GET'])
def export_logs():
    if logs is None:
        return jsonify({'status': 'error', 'message': 'Database not connected'}), 500
    try:
        cursor = logs.find().sort([('timestamp', -1)])
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Timestamp', 'URL', 'Method', 'Prediction'])
        for log in cursor:
            writer.writerow([
                log.get('timestamp', '').isoformat() if log.get('timestamp') else '',
                log.get('URL', ''),
                log.get('Method', ''),
                log.get('prediction', '')
            ])
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={"Content-Disposition": "attachment;filename=waf-logs.csv"}
        )
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    if logs is None:
        return jsonify({'status': 'error', 'message': 'Database not connected'}), 500
    try:
        total_requests = logs.count_documents({})
        malicious_count = logs.count_documents({'prediction': 'blocked'})
        safe_count = logs.count_documents({'prediction': 'allowed'})
        # Attack type frequency (use attack_type if present)
        attack_types = {}
        for log in logs.find({}, {'attack_type': 1}):
            atype = log.get('attack_type', 'unknown')
            attack_types[atype] = attack_types.get(atype, 0) + 1
        success_rate = (safe_count / total_requests * 100) if total_requests > 0 else 0
        return jsonify({
            'total_requests': total_requests,
            'malicious_count': malicious_count,
            'safe_count': safe_count,
            'attack_types': attack_types,
            'success_rate': success_rate
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# --- SOCKET.IO EVENTS ---
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'message': 'Connected to WAF SocketIO'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)