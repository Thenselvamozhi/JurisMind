import joblib
import os
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../data/case_model.pkl")
ENCODER_PATH = os.path.join(os.path.dirname(__file__), "../data/label_encoder.pkl")

# Lazy load
_model = None
_encoder = None


def _load_model():
    global _model, _encoder
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                "Model not found. Please run: python ml_model/train_model.py"
            )
        _model = joblib.load(MODEL_PATH)
        _encoder = joblib.load(ENCODER_PATH)

def predict_case_outcome(case_description: str) -> dict:
    """
    Predicts case outcome from description text.
    Returns outcome label, probability, confidence score.
    """
    _load_model()

    # Get probabilities for all classes
    proba = _model.predict_proba([case_description])[0]
    predicted_index = np.argmax(proba)
    predicted_label = _encoder.inverse_transform([predicted_index])[0]
    confidence = float(proba[predicted_index])

    # Build full probability breakdown
    class_probs = {
        _encoder.inverse_transform([i])[0]: round(float(p) * 100, 1)
        for i, p in enumerate(proba)
    }

    # Interpret outcome
    outcome_map = {
        "win": {"verdict": "Likely Favorable", "color": "green"},
        "lose": {"verdict": "Likely Unfavorable", "color": "red"},
        "guilty": {"verdict": "Likely Guilty Verdict", "color": "red"},
        "acquitted": {"verdict": "Likely Acquittal", "color": "green"},
        "granted": {"verdict": "Likely Granted", "color": "green"},
        "rejected": {"verdict": "Likely Rejected", "color": "red"},
        "uncertain": {"verdict": "Uncertain Outcome", "color": "orange"},
    }

    interpretation = outcome_map.get(
        predicted_label,
        {"verdict": predicted_label.title(), "color": "gray"}
    )

    # Confidence tier
    if confidence >= 0.75:
        confidence_label = "High Confidence"
    elif confidence >= 0.50:
        confidence_label = "Moderate Confidence"
    else:
        confidence_label = "Low Confidence"

    return {
        "outcome": predicted_label,
        "verdict": interpretation["verdict"],
        "color": interpretation["color"],
        "confidence_score": round(confidence * 100, 1),
        "confidence_label": confidence_label,
        "all_probabilities": class_probs,
        "disclaimer": "This prediction is based on ML patterns and is NOT legal advice. Please consult a qualified lawyer."
    }
