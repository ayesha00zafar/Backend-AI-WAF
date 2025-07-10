def analyze_request(req_data):
    """
    Analyze the request and return 'block' or 'allow'.
    Extend this function with your WAF logic.
    """
    if "malicious" in req_data["url"].lower():
        return "block"
    return "allow" 