"""
ML Prediction

Loads the trained model (training it on first use if no model file exists
yet) and predicts a 0-100 plagiarism-likelihood score for a code pair.
"""
import os
import threading
import joblib
import numpy as np

from app.config import settings
from app.ml.preprocessing import build_feature_vector

_model_cache = {}
_lock = threading.Lock()


class MLPredictionError(Exception):
    pass


def _load_model():
    with _lock:
        if "model" in _model_cache:
            return _model_cache["model"]

        if not os.path.exists(settings.MODEL_PATH):
            # Train lazily on first use so the API works out of the box.
            from app.ml.train import train_and_save

            train_and_save(settings.MODEL_PATH)

        bundle = joblib.load(settings.MODEL_PATH)
        _model_cache["model"] = bundle
        return bundle


def predict_ml_score(code_a: str, language: str = "python", code_b: str = None) -> float:
    """Predict plagiarism likelihood (0-100) between code_a and code_b."""
    if code_b is None:
        raise MLPredictionError("code_b is required for pairwise ML prediction.")

    bundle = _load_model()
    model = bundle["model"]

    try:
        vector = build_feature_vector(code_a, code_b, language)
    except Exception as exc:  # noqa: BLE001
        raise MLPredictionError(f"Failed to build features for ML prediction: {exc}") from exc

    X = np.array([vector], dtype=float)
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)[0]
        # proba[1] = probability of class "1" (similar/plagiarized-structure)
        score = float(proba[1]) * 100
    else:
        score = float(model.predict(X)[0]) * 100

    return round(max(0.0, min(100.0, score)), 2)
