import random

def predict_request(features):
    """
    Dummy AI model.
    For now, it randomly predicts the request as malicious or not.
    Later, we can connect a real trained model here.
    """
    prediction = random.choice([0, 1])
    return prediction
