import os
from celery import Celery
from predictor import predict_request
from logger import log_request

app = Celery('waf_tasks', broker=os.getenv("REDIS_URL", "redis://localhost:6379"))

@app.task
def handle_request_task(http_request):
    try:
        prediction = predict_request(http_request)
        log_request(http_request, prediction)
        return prediction
    except Exception as e:
        print(f"Background task failed: {e}")
        return -1
