from pymongo import MongoClient
from datetime import datetime
from preprocess import extract_features
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
import re
import os

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri, tls=True)
db = client['WAF-AI']
collection = db['Queries']
logs = db['RequestLogs']

all_documents = collection.find()

X = []
y = []

for doc in all_documents:
    features = extract_features(doc)
  
    X.append([
        features['url_length'],
        features['special_char_count'],
        features['entropy'],
        features['method'],
        features['content_length'],
        features['script_tag_count'],
        features['alert_count'],
        features['javascript_count'],
        features['on_event_count']
    ])
    y.append(doc.get('classification', 0))  

print(f"Loaded {len(X)} samples for training.")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier()
model.fit(X_train, y_train)

joblib.dump(model, 'waf_model.joblib')

print("Model trained and saved successfully!")

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print("\n Model Evaluation Metrics:")
print(f" Accuracy:  {accuracy:.4f}")
print(f" Precision: {precision:.4f}")
print(f" Recall:    {recall:.4f}")
print(f" F1 Score:  {f1:.4f}")


def log_request(http_request, prediction):
    log_entry = {
        'URL': http_request.get('URL', ''),
        'Method': http_request.get('Method', ''),
        'content': http_request.get('content', ''),
        'prediction': 'blocked' if prediction == 1 else 'allowed',
        'timestamp': datetime.now()
    }
    logs.insert_one(log_entry)
    print(f"Logged: {log_entry}")