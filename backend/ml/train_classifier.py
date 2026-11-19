"""
Train the water body quality classifier using environmental measurements.

Model: Random Forest Classifier
Target: water_quality_status (excellent/good/fair/poor/critical)
Features: ndwi, area_sq_km, water_occurrence_pct, seasonality_months,
          turbidity_ntu, ph, dissolved_oxygen_mgl, chlorophyll_a_ugl, water_body_type_encoded

Evaluated with GroupShuffleSplit on water bodies (wb_index) to guarantee zero temporal leakage.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import joblib
import sys
import warnings
warnings.filterwarnings("ignore")

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

PROC_DIR = Path(__file__).parent.parent.parent / "data" / "processed"
MODEL_DIR = Path(__file__).parent / "models"
MODEL_DIR.mkdir(exist_ok=True)

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import classification_report, accuracy_score

FEATURE_COLS = [
    "ndwi", "area_sq_km", "water_occurrence_pct", "seasonality_months",
    "turbidity_ntu", "ph", "dissolved_oxygen_mgl", "chlorophyll_a_ugl",
    "water_body_type_encoded",
]
TARGET_COL = "target_task2_quality_status"
TYPE_MAP = {"lake": 0, "pond": 1, "reservoir": 2, "river": 3, "wetland": 4, "other": 5}


def load_training_data() -> pd.DataFrame:
    data_path = PROC_DIR / "indexed_waterbody_dataset.csv"
    if not data_path.exists():
        raise FileNotFoundError(f"{data_path} not found. Run export_indexed_dataset.py first.")

    df = pd.read_csv(data_path)
    df["water_body_type_encoded"] = df["target_task1_body_type"].map(TYPE_MAP).fillna(5)

    print(f"  Loaded dataset: {len(df)} records across {df['wb_index'].nunique()} unique water bodies.")
    return df


def train(df: pd.DataFrame):
    X = df[FEATURE_COLS].values
    y = df[TARGET_COL].values
    groups = df["wb_index"].values

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(gss.split(X, y_enc, groups))

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X[train_idx])
    X_test = scaler.transform(X[test_idx])

    y_train = y_enc[train_idx]
    y_test = y_enc[test_idx]

    print(f"\n  Training Random Forest Water Quality classifier...")
    print(f"  Training samples: {len(train_idx)} | Testing samples: {len(test_idx)} (Unseen water bodies)")

    model = RandomForestClassifier(
        n_estimators=180,
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    # Evaluate on truly unseen water bodies
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n  Overall Test Accuracy on Unseen Water Bodies: {acc * 100:.2f}%")
    print("\n  Classification Report (Task 2: Water Quality Status):")
    print(classification_report(y_test, y_pred, target_names=le.classes_, digits=4))

    # Feature importance
    importances = pd.Series(model.feature_importances_, index=FEATURE_COLS).sort_values(ascending=False)
    print("\n  Feature Importances:")
    for feat, imp in importances.items():
        bar = "█" * int(imp * 40)
        print(f"    {feat:<25} {imp*100:6.2f}%  {bar}")

    # Save
    joblib.dump(model, MODEL_DIR / "classifier.pkl")
    joblib.dump(scaler, MODEL_DIR / "scaler.pkl")
    joblib.dump(le, MODEL_DIR / "label_encoder.pkl")
    print(f"\n  ✓ Models saved to {MODEL_DIR}/")


if __name__ == "__main__":
    print("\n🌊 Water Body Quality Classifier Training")
    print("=" * 55)
    df = load_training_data()
    train(df)
    print("\n✅ Training complete.")
