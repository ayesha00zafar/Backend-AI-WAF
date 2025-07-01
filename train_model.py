from pymongo import MongoClient
from preprocess import extract_features
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import numpy as np
import joblib
import os

mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(mongo_uri, tls=True)
db = client['WAF-AI']
collection = db['Queries']

X, y = [], []

for doc in collection.find():
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

print(f"Training on {len(X)} samples...")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestClassifier()
model.fit(X_train, y_train)
joblib.dump(model, 'waf_model.joblib')

y_pred = model.predict(X_test)
print("Model saved. Metrics:")
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Precision:", precision_score(y_test, y_pred))
print("Recall:", recall_score(y_test, y_pred))
print("F1 Score:", f1_score(y_test, y_pred))
