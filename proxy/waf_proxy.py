# proxy/waf_proxy.py
from mitmproxy import http
import sys, os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from predictor import predict_request
from logger import log_request

class WAFProxy:
    def __init__(self):
        logger.info("🚀 WAF Proxy initialized")
        self.stats = {
            'total_requests': 0,
            'blocked_requests': 0,
            'allowed_requests': 0
        }
    
    def request(self, flow: http.HTTPFlow):
        """
        Intercept and analyze each HTTP request
        """
        try:
            self.stats['total_requests'] += 1
            
            # Extract request data
            req_data = {
                "Method": flow.request.method,
                "URL": flow.request.pretty_url,
                "content": flow.request.get_text(),
                "headers": dict(flow.request.headers)
            }
            
            logger.info(f"🔍 Intercepted request #{self.stats['total_requests']}: {req_data['Method']} {req_data['URL']}")
            
            # Get AI prediction
            prediction = predict_request(req_data)
            
            # Log to MongoDB
            log_id = log_request(req_data, prediction)
            
            # Update stats
            if prediction == 1:
                self.stats['blocked_requests'] += 1
                logger.warning(f"🚨 BLOCKING malicious request: {req_data['URL']}")
                
                # Block malicious requests
                flow.response = http.Response.make(
                    403, 
                    b"Request blocked by AI-WAF - Detected as malicious", 
                    {"Content-Type": "text/plain"}
                )
            else:
                self.stats['allowed_requests'] += 1
                logger.info(f"✅ ALLOWING benign request: {req_data['URL']}")
                # Let benign requests pass through
                
            logger.info(f"📊 Stats: Total={self.stats['total_requests']}, Blocked={self.stats['blocked_requests']}, Allowed={self.stats['allowed_requests']}")
            
        except Exception as e:
            logger.error(f"❌ Error processing request: {e}")
            # Default to allow if there's an error
            self.stats['allowed_requests'] += 1
            logger.info("⚠️ Allowing request due to processing error")

addons = [WAFProxy()]