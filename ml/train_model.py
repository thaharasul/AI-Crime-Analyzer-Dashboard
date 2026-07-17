

import json
import pickle

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

from config import CRIME_CSV_PATH, TRAINED_MODEL_PATH, MODEL_METRICS_PATH

FEATURE_COLUMNS = [
    "zone", "severity", "weapon_involved", "day_of_week",
    "hour_of_day", "victim_age",
]
TARGET_COLUMN = "category"


def _build_encoders(df: pd.DataFrame, columns):
    encoders = {}
    for col in columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le
    return encoders


def train():
    df = pd.read_csv(CRIME_CSV_PATH)
    df = df.dropna(subset=FEATURE_COLUMNS + [TARGET_COLUMN]).copy()

    categorical_features = ["zone", "severity", "day_of_week"]
    feature_encoders = _build_encoders(df, categorical_features)

    target_encoder = LabelEncoder()
    df[TARGET_COLUMN] = target_encoder.fit_transform(df[TARGET_COLUMN])

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=250,
        max_depth=12,
        min_samples_leaf=3,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    metrics = {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred, average="weighted", zero_division=0), 4),
        "recall": round(recall_score(y_test, y_pred, average="weighted", zero_division=0), 4),
        "f1_score": round(f1_score(y_test, y_pred, average="weighted", zero_division=0), 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "classes": target_encoder.classes_.tolist(),
        "feature_importance": dict(zip(FEATURE_COLUMNS, model.feature_importances_.round(4).tolist())),
        "train_size": len(X_train),
        "test_size": len(X_test),
    }

    bundle = {
        "model": model,
        "feature_encoders": feature_encoders,
        "target_encoder": target_encoder,
        "feature_columns": FEATURE_COLUMNS,
    }

    with open(TRAINED_MODEL_PATH, "wb") as f:
        pickle.dump(bundle, f)

    with open(MODEL_METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    print("Model trained.")
    print(f"Accuracy: {metrics['accuracy']}  F1: {metrics['f1_score']}")
    print(f"Saved model -> {TRAINED_MODEL_PATH}")
    print(f"Saved metrics -> {MODEL_METRICS_PATH}")
    return metrics


if __name__ == "__main__":
    train()
