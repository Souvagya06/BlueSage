"""
Train the Water-Body Type Classifier (Task 1).
Identifies whether a water body is a lake, pond, reservoir, wetland, or river.
Trained on exported indexed dataset using Random Forest.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import joblib

PROC_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "processed"
MODEL_DIR = Path(__file__).resolve().parent / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


def train_body_type_model():
    csv_path = PROC_DIR / "indexed_waterbody_dataset.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"{csv_path} not found. Run export_indexed_dataset.py first.")

    df = pd.read_csv(csv_path)
    feature_cols = ["area_sq_km", "water_occurrence_pct", "seasonality_months", "ndwi"]
    target_col = "target_task1_body_type"

    X = df[feature_cols].values
    y = df[target_col].values

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_enc, test_size=0.2, random_state=42, stratify=y_enc
    )

    print("\n🌊 Training Water-Body Type Classifier (Task 1)...")
    clf = RandomForestClassifier(n_estimators=150, max_depth=12, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    print("\nClassification Report (Task 1: Water-Body Type):")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    # Save models
    joblib.dump(clf, MODEL_DIR / "body_type_classifier.pkl")
    joblib.dump(scaler, MODEL_DIR / "body_type_scaler.pkl")
    joblib.dump(le, MODEL_DIR / "body_type_encoder.pkl")
    print(f"✓ Saved body-type classifier to {MODEL_DIR}/body_type_classifier.pkl")


if __name__ == "__main__":
    train_body_type_model()

