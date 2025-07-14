from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import json
import csv
import io
from datetime import datetime, timedelta
import random

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Mock data storage
logs_data = []
proxy_status = "stopped"

# Generate mock logs
def generate_mock_logs():
    global logs_data
    attack_types = ['SQLi', 'XSS', 'CSRF', 'LFI', 'RCE', 'Normal']
    methods = ['GET', 'POST', 'PUT', 'DELETE']
    ips = ['192.168.1.100', '10.0.0.50', '203.0.113.25', '172.16.0.75', '198.51.100.10']
    
    for i in range(50):
        timestamp = datetime.now() - timedelta(minutes=random.randint(1, 60))
        attack_type = random.choice(attack_types)
        is_malicious = attack_type != 'Normal'
        
        log = {
            'id': i + 1,
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'ipAddress': random.choice(ips),
            'url': f'https://example.com/{random.choice(["login", "api/users", "search", "products", "admin"])}',
            'method': random.choice(methods),
            'label': 'Malicious' if is_malicious else 'Safe',
            'type': attack_type,
            'status': 'Blocked' if is_malicious else 'Allowed'
        }
        logs_data.append(log)

# Initialize mock data
generate_mock_logs()

@app.route('/api/logs')
def get_logs():
    """Get paginated logs"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    start = (page - 1) * per_page
    end = start + per_page
    
    return jsonify({
        'logs': logs_data[start:end],
        'total': len(logs_data),
        'page': page,
        'per_page': per_page
    })

@app.route('/api/logs', methods=['DELETE'])
def clear_logs():
    """Clear all logs"""
    global logs_data
    logs_data = []
    socketio.emit('logs_cleared', {'message': 'All logs cleared'})
    return jsonify({'message': 'Logs cleared successfully'})

@app.route('/api/logs/export')
def export_logs():
    """Export logs as CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Timestamp', 'IP Address', 'URL', 'Method', 'Label', 'Type', 'Status'])
    
    # Write data
    for log in logs_data:
        writer.writerow([
            log['timestamp'],
            log['ipAddress'],
            log['url'],
            log['method'],
            log['label'],
            log['type'],
            log['status']
        ])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'waf-logs-{datetime.now().strftime("%Y%m%d-%H%M%S")}.csv'
    )

@app.route('/api/proxy/<action>', methods=['POST'])
def proxy_control(action):
    """Control proxy start/stop"""
    global proxy_status
    
    if action == 'start':
        proxy_status = 'running'
        socketio.emit('proxy_status_changed', {'status': 'running'})
        return jsonify({'message': 'Proxy started successfully', 'status': 'running'})
    elif action == 'stop':
        proxy_status = 'stopped'
        socketio.emit('proxy_status_changed', {'status': 'stopped'})
        return jsonify({'message': 'Proxy stopped successfully', 'status': 'stopped'})
    else:
        return jsonify({'error': 'Invalid action'}), 400

@app.route('/api/stats')
def get_stats():
    """Get attack statistics"""
    total_requests = len(logs_data)
    malicious_count = len([log for log in logs_data if log['label'] == 'Malicious'])
    safe_count = total_requests - malicious_count
    
    # Attack type distribution
    attack_types = {}
    for log in logs_data:
        attack_type = log['type']
        attack_types[attack_type] = attack_types.get(attack_type, 0) + 1
    
    return jsonify({
        'total_requests': total_requests,
        'malicious_count': malicious_count,
        'safe_count': safe_count,
        'attack_types': attack_types,
        'success_rate': ((safe_count / total_requests) * 100) if total_requests > 0 else 0
    })

@app.route('/api/status')
def get_status():
    """Get system status"""
    return jsonify({
        'proxy_status': proxy_status,
        'database': 'connected',
        'ai_model': 'loaded',
        'cache': 'active'
    })

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'message': 'Connected to WAF Dashboard'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def add_new_log():
    """Simulate adding new logs periodically"""
    global logs_data
    
    attack_types = ['SQLi', 'XSS', 'CSRF', 'LFI', 'RCE', 'Normal']
    methods = ['GET', 'POST', 'PUT', 'DELETE']
    ips = ['192.168.1.100', '10.0.0.50', '203.0.113.25', '172.16.0.75', '198.51.100.10']
    
    attack_type = random.choice(attack_types)
    is_malicious = attack_type != 'Normal'
    
    new_log = {
        'id': len(logs_data) + 1,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'ipAddress': random.choice(ips),
        'url': f'https://example.com/{random.choice(["login", "api/users", "search", "products", "admin"])}',
        'method': random.choice(methods),
        'label': 'Malicious' if is_malicious else 'Safe',
        'type': attack_type,
        'status': 'Blocked' if is_malicious else 'Allowed'
    }
    
    logs_data.append(new_log)
    
    # Emit to all connected clients
    socketio.emit('new_log', new_log)
    
    # Keep only last 1000 logs
    if len(logs_data) > 1000:
        logs_data.pop(0)

if __name__ == '__main__':
    # Start periodic log generation
    import threading
    import time
    
    def generate_logs_periodically():
        while True:
            time.sleep(5)  # Add new log every 5 seconds
            add_new_log()
    
    log_thread = threading.Thread(target=generate_logs_periodically, daemon=True)
    log_thread.start()
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True) 