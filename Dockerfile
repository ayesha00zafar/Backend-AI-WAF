# Use a slim Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

COPY requirements.txt .


RUN pip install --upgrade pip && pip install -r requirements.txt


COPY . .


CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "waf_proxy:app"]


