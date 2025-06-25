import joblib
from preprocess import extract_features

model = joblib.load('waf_model.joblib')

def predict_request(http_request):
    features = extract_features(http_request)

    feature_vector = [
        features['url_length'],
        features['special_char_count'],
        features['entropy'],
        features['method'],
        features['content_length'],
        features['script_tag_count'],
        features['alert_count'],
        features['javascript_count'],
        features['on_event_count']
    ]

    if features['script_tag_count'] > 0 or features['alert_count'] > 0 or features['javascript_count'] > 0 or features['on_event_count'] > 0:
        return 1 

    prediction = model.predict([feature_vector])[0]
    return prediction
