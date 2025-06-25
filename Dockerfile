# ✅ 1. Use an official Python base image
FROM python:3.10-slim

# ✅ 2. Set the working directory inside the container
WORKDIR /app

# ✅ 3. Copy everything from your local project into the container
COPY . .

# ✅ 4. Upgrade pip and install Python packages from requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# ✅ 5. Expose the port Flask will run on (5000)
EXPOSE 5000

# ✅ 6. Run your WAF backend
CMD ["python", "waf_proxy.py"]
