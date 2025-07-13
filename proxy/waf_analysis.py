import re
import json
import os
import time
from collections import defaultdict, deque
from logger import log_block, log_allow

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../waf_config.json')

_config_cache = None
_patterns_cache = None

# In-memory rate limit store (for production, use Redis or similar)
_ip_request_log = defaultdict(lambda: deque())
_ip_blocked_until = defaultdict(float)

def load_config():
    global _config_cache
    with open(CONFIG_PATH, 'r') as f:
        _config_cache = json.load(f)
    return _config_cache

def get_config():
    global _config_cache
    if _config_cache is None:
        return load_config()
    return _config_cache

def compile_patterns():
    global _patterns_cache
    config = get_config()
    _patterns_cache = {
        'SQLI_PATTERNS': [re.compile(p, re.IGNORECASE) for p in config['sqli_patterns']],
        'XSS_PATTERNS': [re.compile(p, re.IGNORECASE) for p in config['xss_patterns']]
    }
    return _patterns_cache

def get_patterns():
    global _patterns_cache
    if _patterns_cache is None:
        return compile_patterns()
    return _patterns_cache

def reload_config():
    """Reload config and recompile patterns. Call this if you want to hot-reload config at runtime."""
    load_config()
    compile_patterns()

def is_rate_limited(ip, config):
    now = time.time()
    window = 60  # seconds
    rate_limit = config.get('rate_limit', {})
    max_requests = rate_limit.get('requests_per_minute', 60)
    block_duration = rate_limit.get('block_duration_seconds', 300)
    # Remove old timestamps
    req_log = _ip_request_log[ip]
    while req_log and now - req_log[0] > window:
        req_log.popleft()
    # Check if currently blocked
    if now < _ip_blocked_until[ip]:
        return True
    # Add current request
    req_log.append(now)
    if len(req_log) > max_requests:
        _ip_blocked_until[ip] = now + block_duration
        return True
    return False

def matches_patterns(patterns, text):
    for pattern in patterns:
        if pattern.search(text):
            return True
    return False

def score_request(req_data):
    config = get_config()
    patterns = get_patterns()
    score = 0
    reasons = []

    url = req_data.get("url", "")
    headers = req_data.get("headers", {})
    body = req_data.get("body", "")
    ip = req_data.get("ip", "")

    # Rate limiting
    if is_rate_limited(ip, config):
        score += config['rate_limit'].get('rate_limit_score', 5)
        reasons.append("Rate limit exceeded for IP")

    # IP/domain blacklist
    if any(domain in url for domain in config['malicious_domains']):
        score += config['weights']['malicious_domain']
        reasons.append("Known malicious domain")
    if ip in config['malicious_ips']:
        score += config['weights']['malicious_ip']
        reasons.append("Known malicious IP")

    # Sensitive endpoints
    if any(endpoint in url for endpoint in config['sensitive_endpoints']):
        score += config['weights']['sensitive_endpoint']
        reasons.append("Sensitive endpoint")

    # Contextual pattern matching
    if matches_patterns(patterns['SQLI_PATTERNS'], url):
        score += config['weights'].get('sqli_url', 0)
        reasons.append("SQLi pattern in URL")
    if matches_patterns(patterns['XSS_PATTERNS'], url):
        score += config['weights'].get('xss_url', 0)
        reasons.append("XSS pattern in URL")

    for value in headers.values():
        if matches_patterns(patterns['SQLI_PATTERNS'], value):
            score += config['weights'].get('sqli_header', 0)
            reasons.append("SQLi pattern in header")
        if matches_patterns(patterns['XSS_PATTERNS'], value):
            score += config['weights'].get('xss_header', 0)
            reasons.append("XSS pattern in header")

    if matches_patterns(patterns['SQLI_PATTERNS'], body):
        score += config['weights'].get('sqli_body', 0)
        reasons.append("SQLi pattern in body")
    if matches_patterns(patterns['XSS_PATTERNS'], body):
        score += config['weights'].get('xss_body', 0)
        reasons.append("XSS pattern in body")

    return score, reasons

def analyze_request(req_data):
    config = get_config()
    score, reasons = score_request(req_data)
    log_data = {
        'score': score,
        'reasons': reasons,
        'request': req_data
    }
    if score >= config['block_threshold']:
        log_block(f"BLOCKED | Score: {score} | Reasons: {reasons}", req_data)
        return "block"
    else:
        log_allow(req_data)
        return "allow"
