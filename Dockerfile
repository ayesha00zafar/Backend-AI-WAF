FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 8080

ENTRYPOINT ["bash", "-c"]
CMD ["python waf_proxy.py"]





