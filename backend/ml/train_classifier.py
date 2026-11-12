"""
Train the water body quality classifier using real USGS water quality data.

Model: Random Forest Classifier
Target: water_quality_status (excellent/good/fair/poor/critical)
Features: ndwi, area_sq_km, water_occurrence_pct, seasonality_months,
          turbidity_ntu, ph, dissolved_oxygen_mgl, chlorophyll_a_ugl, water_body_type

Run:
    cd backend
    python ml/train_classifier.py
"""
import pandas as pd
import numpy as np
from pathlib import Path
import joblib
import sys

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
import warnings
warnings.filterwarnings("ignore")

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

PROC_DIR = Path(__file__).parent.parent.parent / "data" / "processed"
MODEL_DIR = Path(__file__).parent / "models"
MODEL_DIR.mkdir(exist_ok=True)

FEATURE_COLS = [
    "ndwi", "area_sq_km", "water_occurrence_pct", "seasonality_months",
    "turbidity_ntu", "ph", "dissolved_oxygen_mgl", "chlorophyll_a_ugl",
    "water_body_type_encoded",
]
TARGET_COL = "water_quality_status"

TYPE_MAP = {"lake": 0, "pond": 1, "reservoir": 2, "river": 3, "wetland": 4, "other": 5}


def load_training_data() -> pd.DataFrame:
    obs_path = PROC_DIR / "temporal_observations.csv"
    wb_path = PROC_DIR / "water_bodies.csv"

    if not obs_path.exists():
        raise FileNotFoundError(
            "data/processed/temporal_observations.csv not found.\n"
            "Run: python data_pipeline/download_data.py && python data_pipeline/preprocess.py"
        )

    obs = pd.read_csv(obs_path)
    wb = pd.read_csv(wb_path, index_col="wb_index")

    # Merge to get water_body_type
    obs["wb_index"] = obs["wb_index"].astype(int)
    merged = obs.merge(
        wb[["water_body_type"]].reset_index(),
        left_on="wb_index", right_on="wb_index",
        how="left"
    )

    merged["water_body_type_encoded"] = merged["water_body_type"].map(TYPE_MAP).fillna(5)

    # Drop rows missing target or ndwi
    merged = merged.dropna(subset=[TARGET_COL, "ndwi"])

    # Fill missing feature values with column median (not synthetic — median imputation)
    for col in FEATURE_COLS:
        if col in merged.columns:
            merged[col] = merged[col].fillna(merged[col].median())

    print(f"  Training data: {len(merged)} records")
    print(f"  Class distribution:\n{merged[TARGET_COL].value_counts()}")
    return merged


def train(df: pd.DataFrame):
    X = df[FEATURE_COLS].values
    y = df[TARGET_COL].values

    # Encode labels
    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train / test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_enc, test_size=0.2, random_state=42, stratify=y_enc
    )

    print(f"\n  Training Random Forest classifier...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    print("\n  Classification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    # Cross-validation
    cv_scores = cross_val_score(model, X_scaled, y_enc, cv=5, scoring="f1_weighted")
    print(f"  Cross-val F1 (weighted): {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    # Feature importance
    importances = pd.Series(model.feature_importances_, index=FEATURE_COLS)
    print("\n  Feature Importances:")
    print(importances.sort_values(ascending=False).to_string())

    # Save
    joblib.dump(model, MODEL_DIR / "classifier.pkl")
    joblib.dump(scaler, MODEL_DIR / "scaler.pkl")
    joblib.dump(le, MODEL_DIR / "label_encoder.pkl")
    print(f"\n  ✓ Models saved to {MODEL_DIR}/")


if __name__ == "__main__":
    print("\n🌊 Water Body Quality Classifier Training")
    print("=" * 50)
    df = load_training_data()
    train(df)
    print("\n✅ Training complete.")

