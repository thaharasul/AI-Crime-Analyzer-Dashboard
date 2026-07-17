

import json
import pickle

import numpy as np
import pandas as pd

from config import TRAINED_MODEL_PATH, MODEL_METRICS_PATH

_bundle = None


def _load_bundle():
    global _bundle
    if _bundle is None:
        if not TRAINED_MODEL_PATH.exists():
            raise FileNotFoundError(
                "No trained model found. Run `python -m ml.train_model` first."
            )
        with open(TRAINED_MODEL_PATH, "rb") as f:
            _bundle = pickle.load(f)
    return _bundle


def get_metrics():
    if not MODEL_METRICS_PATH.exists():
        return None
    with open(MODEL_METRICS_PATH) as f:
        return json.load(f)


def _encode_input(raw: dict, bundle: dict) -> pd.DataFrame:
    encoded = {}

    for col in bundle["feature_columns"]:
        if col in bundle["feature_encoders"]:
            encoder = bundle["feature_encoders"][col]
            value = str(raw.get(col))
            if value not in encoder.classes_:
                # Unseen category at inference time - fall back to the
                # most frequent class rather than crashing the request.
                value = encoder.classes_[0]
            encoded[col] = float(encoder.transform([value])[0])
        else:
            encoded[col] = float(raw.get(col, 0))

    df = pd.DataFrame([encoded])
    return df[bundle["feature_columns"]]


def _risk_label(top_probability: float) -> str:
    if top_probability >= 0.65:
        return "High"
    if top_probability >= 0.4:
        return "Medium"
    return "Low"


def predict(raw_input: dict) -> dict:
    """
    raw_input keys: zone, severity, day_of_week, weapon_involved,
    hour_of_day, victim_age
    """
    bundle = _load_bundle()
    X = _encode_input(raw_input, bundle)

    model = bundle["model"]
    target_encoder = bundle["target_encoder"]

    probabilities = model.predict_proba(X)[0]
    top_idx = int(np.argmax(probabilities))
    predicted_category = target_encoder.inverse_transform([top_idx])[0]
    confidence = float(round(probabilities[top_idx], 4))

    ranked = sorted(
        zip(target_encoder.classes_, probabilities.round(4).tolist()),
        key=lambda pair: pair[1],
        reverse=True,
    )

    return {
        "predicted_category": predicted_category,
        "confidence": confidence,
        "risk_level": _risk_label(confidence),
        "probability_breakdown": [
            {"category": cat, "probability": prob} for cat, prob in ranked
        ],
    }
