"""
Model Training

Trains a Random Forest classifier (with Logistic Regression / SVM offered
for comparison) on the generated dataset, using a GROUP-aware split so that
transformed variants of the same base program never appear on both sides of
the train/test boundary (this is what "avoid data leakage" means here).

Run directly:
    python -m app.ml.train
"""
import json
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score,
)

from app.config import settings
from app.ml.dataset_generator import generate_dataset
from app.ml.preprocessing import build_dataset_matrix, VECTOR_FEATURE_NAMES


def evaluate(model, X_test, y_test) -> dict:
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else y_pred

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1_score": f1_score(y_test, y_pred, zero_division=0),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
    }
    try:
        metrics["roc_auc"] = roc_auc_score(y_test, y_proba)
    except ValueError:
        metrics["roc_auc"] = None
    return metrics


def train_and_save(model_path: str = None) -> dict:
    model_path = model_path or settings.MODEL_PATH

    pairs = generate_dataset()
    X, y, groups = build_dataset_matrix(pairs)
    X = np.array(X, dtype=float)
    y = np.array(y, dtype=int)
    groups = np.array(groups)

    # Group-aware split: variants of the same base_problem stay together.
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=42)
    train_idx, test_idx = next(splitter.split(X, y, groups))
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

    candidates = {
        "random_forest": RandomForestClassifier(
            n_estimators=200, max_depth=8, random_state=42, class_weight="balanced"
        ),
        "logistic_regression": LogisticRegression(max_iter=2000, class_weight="balanced"),
        "svm": SVC(probability=True, class_weight="balanced", random_state=42),
    }

    results = {}
    for model_name, model in candidates.items():
        if len(np.unique(y_train)) < 2 or len(X_train) < 4:
            # Not enough data/classes to fit meaningfully — skip gracefully.
            continue
        model.fit(X_train, y_train)
        results[model_name] = {
            "model": model,
            "metrics": evaluate(model, X_test, y_test) if len(X_test) > 0 else {},
        }

    if not results:
        raise RuntimeError("Not enough data to train any model.")

    # Primary model: Random Forest, as specified.
    best_name = "random_forest" if "random_forest" in results else next(iter(results))
    best_model = results[best_name]["model"]

    joblib.dump(
        {
            "model": best_model,
            "feature_names": VECTOR_FEATURE_NAMES,
            "model_name": best_name,
        },
        model_path,
    )

    report = {name: r["metrics"] for name, r in results.items()}
    report_path = model_path.replace(".joblib", "_metrics.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    return report


if __name__ == "__main__":
    report = train_and_save()
    print(json.dumps(report, indent=2, default=str))
