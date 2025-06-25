import re
import math
from collections import Counter

def calculate_entropy(string):
    counter = Counter(string)
    total_length = len(string)
    if total_length == 0:
        return 0
    entropy = -sum((count / total_length) * math.log2(count / total_length) for count in counter.values())
    return entropy

def extract_features(document):
    url = document.get('URL', '')
    method = document.get('Method', 'GET')
    content = document.get('content', '')

    features = {
        'url_length': len(url),
        'special_char_count': len(re.findall(r"[\'\"<>=]", url)),
        'entropy': calculate_entropy(url),
        'method': 1 if method == 'POST' else 0,
        'content_length': len(content),
        'script_tag_count': len(re.findall(r"<script.*?>", url, re.IGNORECASE)),
        'alert_count': len(re.findall(r"alert\s*\(", url, re.IGNORECASE)),
        'javascript_count': len(re.findall(r"javascript:", url, re.IGNORECASE)),
        'on_event_count': len(re.findall(r"on\w+\s*=", url, re.IGNORECASE))
    }

    return features


