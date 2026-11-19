"""
Train the Water-Body Type Classifier (Task 1).
Identifies whether a water body is a lake, pond, reservoir, wetland, or river.
Trained using Group-Stratified Cross-Validation on water body IDs (wb_index)
to prevent temporal data leakage across observation years.
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
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score


def train_body_type_model():
    csv_path = PROC_DIR / "indexed_waterbody_dataset.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"{csv_path} not found. Run export_indexed_dataset.py first.")

    df = pd.read_csv(csv_path)
    feature_cols = [
        "area_sq_km",
        "perimeter_km",
        "elongation_ratio",
        "water_occurrence_pct",
        "seasonality_months",
        "ndwi",
        "turbidity_ntu",
    ]
    target_col = "target_task1_body_type"

    X = df[feature_cols].values
    y = df[target_col].values
    groups = df["wb_index"].values

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    # GroupShuffleSplit ensures entire 11-year observation histories of held-out
    # water bodies are isolated to test set only (preventing temporal data leakage)
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(gss.split(X, y_enc, groups))

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X[train_idx])
    X_test = scaler.transform(X[test_idx])

    y_train = y_enc[train_idx]
    y_test = y_enc[test_idx]

    print(f"\n🌊 Training Water-Body Type Classifier (Task 1)...")
    print(f"  Training samples: {len(train_idx)} | Testing samples: {len(test_idx)} (Unseen water bodies)")

    clf = RandomForestClassifier(
        n_estimators=150,
        max_depth=10,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n  Overall Test Accuracy on Unseen Water Bodies: {acc * 100:.2f}%")
    print("\nClassification Report (Task 1: Water-Body Type):")
    print(classification_report(y_test, y_pred, target_names=le.classes_, digits=4))

    # Save models
    joblib.dump(clf, MODEL_DIR / "body_type_classifier.pkl")
    joblib.dump(scaler, MODEL_DIR / "body_type_scaler.pkl")
    joblib.dump(le, MODEL_DIR / "body_type_encoder.pkl")
    print(f"✓ Saved body-type classifier to {MODEL_DIR}/body_type_classifier.pkl")


if __name__ == "__main__":
    train_body_type_model()
