def make_decision(prediction):
    """
    Simple decision function:
    If prediction is 1 (malicious), block the request.
    If prediction is 0 (benign), allow the request.
    """
    if prediction == 1:
        return 'block'
    else:
        return 'allow'
