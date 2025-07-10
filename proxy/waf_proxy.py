from mitmproxy import http
from waf_analysis import analyze_request
from logger import log_request
from cache import check_cache, update_cache

class WAFProxy:
    def request(self, flow: http.HTTPFlow):
        req_data = {
            "method": flow.request.method,
            "url": flow.request.pretty_url,
            "headers": dict(flow.request.headers),
            "body": flow.request.get_text()
        }

        # Check Redis cache first
        cached_result = check_cache(req_data)
        if cached_result is not None:
            action = cached_result
        else:
            action = analyze_request(req_data)
            update_cache(req_data, action)

        log_request(req_data, action)

        if action == "block":
            flow.response = http.Response.make(
                403, b"Blocked by AI-WAF", {"Content-Type": "text/plain"}
            )

addons = [WAFProxy()] 