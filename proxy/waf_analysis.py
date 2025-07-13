import re
import datetime
from logger import log_block, log_allow

# Example lists (expand as needed)
MALICIOUS_DOMAINS = {"bad-domain.com", "evil.com"}
MALICIOUS_IPS = {"123.45.67.89", "10.0.0.66"}
SENSITIVE_ENDPOINTS = ["/admin", "/config", "/wp-admin", "/.env", "/phpmyadmin"]

# Simple regexes for SQLi and XSS (expand for production)
SQLI_PATTERNS = [
    r"(\%27)|(\')|(\-\-)|(\%23)|(#)",  # SQL meta-characters
    r"(\bOR\b|\bAND\b).*(=|LIKE)",     # SQL logic
    r"UNION(\s)+SELECT",                 # UNION SELECT
]
XSS_PATTERNS = [
    r"<script.*?>",                    # Script tags
    r"on\w+\s*=",                      # Inline event handlers
    r"javascript:",                    # JS URIs
]

def matches_patterns(patterns, text):
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def analyze_request(req_data):
    """
    Analyze the request and return 'block' or 'allow'.
    """
    url = req_data.get("url", "")
    headers = req_data.get("headers", {})
    body = req_data.get("body", "")
    ip = req_data.get("ip", "")

    # 1. Block known malicious domains/IPs
    if any(domain in url for domain in MALICIOUS_DOMAINS):
        log_block("Malicious domain", req_data)
        return "block"
    if ip in MALICIOUS_IPS:
        log_block("Malicious IP", req_data)
        return "block"

    # 2. Block sensitive endpoints
    if any(endpoint in url for endpoint in SENSITIVE_ENDPOINTS):
        log_block("Sensitive endpoint", req_data)
        return "block"

    # 3. Block SQLi/XSS in URL, headers, or body
    if matches_patterns(SQLI_PATTERNS, url):
        log_block("SQLi pattern in URL", req_data)
        return "block"
    if matches_patterns(XSS_PATTERNS, url):
        log_block("XSS pattern in URL", req_data)
        return "block"
    for value in headers.values():
        if matches_patterns(SQLI_PATTERNS, value):
            log_block("SQLi pattern in header", req_data)
            return "block"
        if matches_patterns(XSS_PATTERNS, value):
            log_block("XSS pattern in header", req_data)
            return "block"
    if matches_patterns(SQLI_PATTERNS, body):
        log_block("SQLi pattern in body", req_data)
        return "block"
    if matches_patterns(XSS_PATTERNS, body):
        log_block("XSS pattern in body", req_data)
        return "block"

    # 4. Allow otherwise
    log_allow(req_data)
    return "allow" 