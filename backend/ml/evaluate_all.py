"""
Comprehensive Model Evaluation Script
======================================
Prints realistic, publication-grade classification reports (F1-score, precision, recall, accuracy),
confusion matrices, and feature importances evaluated strictly on unseen water bodies
(GroupShuffleSplit by wb_index) to prevent temporal data leakage.

Run:
    backend\\venv\\Scripts\\python.exe backend\\ml\\evaluate_all.py
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import joblib

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
PROC_DIR = ROOT_DIR / "data" / "processed"
MODEL_DIR = ROOT_DIR / "backend" / "ml" / "models"

from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
from sklearn.model_selection import GroupShuffleSplit


def evaluate_task1():
    print("\n" + "=" * 70)
    print("  📊 TASK 1: WATER-BODY TYPE CLASSIFIER EVALUATION")
    print("     (Evaluated on Unseen Water Bodies - GroupShuffleSplit Test Set)")
    print("=" * 70)

    model_path = MODEL_DIR / "body_type_classifier.pkl"
    scaler_path = MODEL_DIR / "body_type_scaler.pkl"
    encoder_path = MODEL_DIR / "body_type_encoder.pkl"
    data_path = PROC_DIR / "indexed_waterbody_dataset.csv"

    if not all([model_path.exists(), scaler_path.exists(), encoder_path.exists(), data_path.exists()]):
        print("❌ Missing model artifacts or data. Run training script first.")
        return

    clf = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    le = joblib.load(encoder_path)
    df = pd.read_csv(data_path)

    features = [
        "area_sq_km",
        "perimeter_km",
        "elongation_ratio",
        "water_occurrence_pct",
        "seasonality_months",
        "ndwi",
        "turbidity_ntu",
    ]
    target = "target_task1_body_type"

    X = df[features].values
    y = df[target].values
    groups = df["wb_index"].values
    y_enc = le.transform(y)

    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    _, test_idx = next(gss.split(X, y_enc, groups))

    X_test = scaler.transform(X[test_idx])
    y_test = y_enc[test_idx]
    y_pred = clf.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    f1_weighted = f1_score(y_test, y_pred, average="weighted")
    f1_macro = f1_score(y_test, y_pred, average="macro")

    print(f"\n  Unseen Test Water Bodies: {df.iloc[test_idx]['wb_index'].nunique()}")
    print(f"  Total Test Observations:  {len(test_idx)}")
    print(f"  Overall Accuracy:         {acc * 100:.2f}%")
    print(f"  Weighted F1-Score:        {f1_weighted:.4f}")
    print(f"  Macro F1-Score:           {f1_macro:.4f}\n")

    print("  Detailed Classification Report (Precision, Recall, F1-Score):")
    print("  " + "-" * 66)
    report = classification_report(y_test, y_pred, target_names=le.classes_, digits=4)
    for line in report.split("\n"):
        print(f"  {line}")

    print("\n  Confusion Matrix:")
    print("  " + "-" * 66)
    cm = confusion_matrix(y_test, y_pred)
    cm_df = pd.DataFrame(cm, index=[f"True {c}" for c in le.classes_], columns=[f"Pred {c}" for c in le.classes_])
    print(cm_df.to_string().replace("\n", "\n  "))


def evaluate_task2():
    print("\n" + "=" * 70)
    print("  📊 TASK 2: WATER QUALITY STATUS CLASSIFIER EVALUATION")
    print("     (Evaluated on Unseen Water Bodies - GroupShuffleSplit Test Set)")
    print("=" * 70)

    model_path = MODEL_DIR / "classifier.pkl"
    scaler_path = MODEL_DIR / "scaler.pkl"
    encoder_path = MODEL_DIR / "label_encoder.pkl"
    data_path = PROC_DIR / "indexed_waterbody_dataset.csv"

    if not all([model_path.exists(), scaler_path.exists(), encoder_path.exists(), data_path.exists()]):
        print("❌ Missing model artifacts or data. Run training script first.")
        return

    clf = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    le = joblib.load(encoder_path)
    df = pd.read_csv(data_path)

    type_map = {"lake": 0, "pond": 1, "reservoir": 2, "river": 3, "wetland": 4, "other": 5}
    df["water_body_type_encoded"] = df["target_task1_body_type"].map(type_map).fillna(5)

    features = [
        "ndwi", "area_sq_km", "water_occurrence_pct", "seasonality_months",
        "turbidity_ntu", "ph", "dissolved_oxygen_mgl", "chlorophyll_a_ugl",
        "water_body_type_encoded",
    ]
    target = "target_task2_quality_status"

    X = df[features].values
    y = df[target].values
    groups = df["wb_index"].values
    y_enc = le.transform(y)

    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    _, test_idx = next(gss.split(X, y_enc, groups))

    X_test = scaler.transform(X[test_idx])
    y_test = y_enc[test_idx]
    y_pred = clf.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    f1_weighted = f1_score(y_test, y_pred, average="weighted")
    f1_macro = f1_score(y_test, y_pred, average="macro")

    print(f"\n  Unseen Test Water Bodies: {df.iloc[test_idx]['wb_index'].nunique()}")
    print(f"  Total Test Observations:  {len(test_idx)}")
    print(f"  Overall Accuracy:         {acc * 100:.2f}%")
    print(f"  Weighted F1-Score:        {f1_weighted:.4f}")
    print(f"  Macro F1-Score:           {f1_macro:.4f}\n")

    print("  Detailed Classification Report (Precision, Recall, F1-Score):")
    print("  " + "-" * 66)
    report = classification_report(y_test, y_pred, target_names=le.classes_, digits=4)
    for line in report.split("\n"):
        print(f"  {line}")

    print("\n  Confusion Matrix:")
    print("  " + "-" * 66)
    cm = confusion_matrix(y_test, y_pred)
    cm_df = pd.DataFrame(cm, index=[f"True {c}" for c in le.classes_], columns=[f"Pred {c}" for c in le.classes_])
    print(cm_df.to_string().replace("\n", "\n  "))

    print("\n  Top Feature Importances:")
    print("  " + "-" * 66)
    fi = pd.Series(clf.feature_importances_, index=features).sort_values(ascending=False)
    for feat, imp in fi.items():
        bar = "█" * int(imp * 40)
        print(f"    {feat:<25} {imp*100:6.2f}%  {bar}")


if __name__ == "__main__":
    evaluate_task1()
    evaluate_task2()
    print("\n" + "=" * 70)
    print("  ✅ All Model Evaluations Completed.")
    print("=" * 70 + "\n")
