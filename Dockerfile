# Use a slim Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the full app
COPY . .

# Run with Gunicorn (production WSGI server)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "waf_proxy:app"]


