# predictor.py
import joblib
from preprocess import extract_features
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    model = joblib.load('waf_model.joblib')
    logger.info("✅ AI Model loaded successfully")
except Exception as e:
    logger.error(f"❌ Failed to load AI model: {e}")
    model = None

def predict_request(http_request):
    """
    Predict if a request is malicious using AI model
    Returns: 1 for malicious, 0 for benign
    """
    try:
        logger.info(f"🔍 Analyzing request: {http_request.get('URL', 'Unknown URL')}")
        
        # Extract features
        features = extract_features(http_request)
        logger.info(f"📊 Extracted features: {features}")
        
        # Create feature vector
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
        
        # Use ML model for prediction
        if model is not None:
            prediction = model.predict([feature_vector])[0]
            logger.info(f"🤖 ML Model prediction: {prediction} (1=malicious, 0=benign)")
        else:
            # Fallback to rule-based if model not available
            logger.warning("⚠️ Using fallback rule-based detection")
            if (features['script_tag_count'] > 0 or 
                features['alert_count'] > 0 or 
                features['javascript_count'] > 0 or 
                features['on_event_count'] > 0):
                prediction = 1
                logger.info("🚨 Rule-based: Detected suspicious patterns")
            else:
                prediction = 0
                logger.info("✅ Rule-based: No suspicious patterns detected")
        
        # Additional safety checks
        url = http_request.get('URL', '').lower()
        if any(pattern in url for pattern in ['<script', 'javascript:', 'alert(', 'onload=']):
            prediction = 1
            logger.warning("🚨 Safety check: Detected obvious malicious patterns")
        
        logger.info(f"🎯 Final prediction: {prediction} ({'BLOCK' if prediction == 1 else 'ALLOW'})")
        return prediction
        
    except Exception as e:
        logger.error(f"❌ Error during prediction: {e}")
        # Default to allow if prediction fails
        return 0