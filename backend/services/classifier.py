"""
Water-body classification service using a trained ML model.
Classifies water bodies into quality status (excellent/good/fair/poor/critical).
"""
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional

MODEL_PATH = Path(__file__).parent.parent / "ml" / "models" / "classifier.pkl"
SCALER_PATH = Path(__file__).parent.parent / "ml" / "models" / "scaler.pkl"
ENCODER_PATH = Path(__file__).parent.parent / "ml" / "models" / "label_encoder.pkl"

BODY_TYPE_MODEL_PATH = Path(__file__).parent.parent / "ml" / "models" / "body_type_classifier.pkl"
BODY_TYPE_SCALER_PATH = Path(__file__).parent.parent / "ml" / "models" / "body_type_scaler.pkl"
BODY_TYPE_ENCODER_PATH = Path(__file__).parent.parent / "ml" / "models" / "body_type_encoder.pkl"

_model = None
_scaler = None
_encoder = None

_bt_model = None
_bt_scaler = None
_bt_encoder = None


def _load_models():
    global _model, _scaler, _encoder
    if _model is None:
        _model = joblib.load(MODEL_PATH)
        _scaler = joblib.load(SCALER_PATH)
        _encoder = joblib.load(ENCODER_PATH)


def classify_water_body(
    ndwi: float,
    area_sq_km: float,
    water_occurrence_pct: Optional[float],
    seasonality_months: Optional[int],
    turbidity_ntu: Optional[float],
    ph: Optional[float],
    dissolved_oxygen_mgl: Optional[float],
    chlorophyll_a_ugl: Optional[float],
    water_body_type: str,
) -> dict:
    """
    Returns predicted quality class and confidence scores.
    """
    if MODEL_PATH.exists() and SCALER_PATH.exists() and ENCODER_PATH.exists():
        _load_models()
        # Feature vector — must match training order
        type_map = {"lake": 0, "pond": 1, "reservoir": 2, "river": 3, "wetland": 4, "other": 5}
        features = np.array([[
            ndwi if ndwi is not None else 0.0,
            area_sq_km if area_sq_km is not None else 0.0,
            water_occurrence_pct if water_occurrence_pct is not None else 50.0,
            seasonality_months if seasonality_months is not None else 6,
            turbidity_ntu if turbidity_ntu is not None else 20.0,
            ph if ph is not None else 7.0,
            dissolved_oxygen_mgl if dissolved_oxygen_mgl is not None else 7.0,
            chlorophyll_a_ugl if chlorophyll_a_ugl is not None else 10.0,
            type_map.get(water_body_type, 5),
        ]])

        features_scaled = _scaler.transform(features)
        pred_encoded = _model.predict(features_scaled)[0]
        pred_label = _encoder.inverse_transform([pred_encoded])[0]

        proba = _model.predict_proba(features_scaled)[0]
        confidence = float(np.max(proba))

        class_probs = {
            _encoder.inverse_transform([i])[0]: float(p)
            for i, p in enumerate(proba)
        }

        return {
            "predicted_quality_status": pred_label,
            "confidence": confidence,
            "class_probabilities": class_probs,
        }

    # ── Fallback Heuristic Classifier (When ML model is not yet trained) ──
    do = dissolved_oxygen_mgl if dissolved_oxygen_mgl is not None else 6.5
    turb = turbidity_ntu if turbidity_ntu is not None else 15.0
    val_ph = ph if ph is not None else 7.2

    if do >= 7.0 and turb <= 10.0 and 6.5 <= val_ph <= 8.5:
        pred_label = "excellent"
        confidence = 0.92
    elif do >= 5.5 and turb <= 20.0 and 6.0 <= val_ph <= 9.0:
        pred_label = "good"
        confidence = 0.85
    elif do >= 4.0 and turb <= 35.0:
        pred_label = "fair"
        confidence = 0.78
    elif do >= 2.5:
        pred_label = "poor"
        confidence = 0.81
    else:
        pred_label = "critical"
        confidence = 0.89

    classes = ["excellent", "good", "fair", "poor", "critical"]
    remaining = (1.0 - confidence) / (len(classes) - 1)
    class_probs = {c: (confidence if c == pred_label else round(remaining, 3)) for c in classes}

def classify_water_body_type(
    area_sq_km: float,
    water_occurrence_pct: Optional[float] = None,
    seasonality_months: Optional[int] = None,
    perimeter_km: Optional[float] = None,
    elongation_ratio: Optional[float] = None,
    ndwi: Optional[float] = 0.40,
    turbidity_ntu: Optional[float] = None,
    name: Optional[str] = None,
    is_artificial: Optional[bool] = False,
) -> dict:
    """
    Identifies whether a water body is a pond, lake, reservoir, wetland, or river.
    Uses trained Random Forest classifier with geomorphological & hydrological indices.
    """
    global _bt_model, _bt_scaler, _bt_encoder
    occ = water_occurrence_pct if water_occurrence_pct is not None else 85.0
    season = seasonality_months if seasonality_months is not None else 10
    ndwi_val = ndwi if ndwi is not None else 0.40

    # Derive geomorphological elongation ratio and perimeter if not explicitly provided
    if elongation_ratio is not None:
        elongation = elongation_ratio
        if perimeter_km is None:
            perimeter_km = round(elongation * 2.0 * np.sqrt(3.14159 * max(0.001, area_sq_km)), 2)
    elif perimeter_km is not None and perimeter_km > 0:
        elongation = round(perimeter_km / (2.0 * np.sqrt(3.14159 * max(0.001, area_sq_km))), 2)
    else:
        # Physical & semantic prior derivation from hydrologic features
        name_lower = str(name).lower() if name else ""
        if any(kw in name_lower for kw in ["river", "reach", "creek", "canal", "stream", "nadi", "ganga", "hooghly", "yamuna", "danube", "rhine", "amazon", "nile", "mississippi"]):
            elongation = 5.8
        elif is_artificial or any(kw in name_lower for kw in ["reservoir", "dam", "sagar", "barrage"]):
            elongation = 2.8
        elif area_sq_km < 0.08 or any(kw in name_lower for kw in ["pond", "puddle", "tank", "jheel", "sarobar"]):
            elongation = 1.15
        elif (water_occurrence_pct is not None and water_occurrence_pct < 70) or (seasonality_months is not None and seasonality_months <= 7) or ("wetland" in name_lower):
            elongation = 2.4
        else:
            elongation = 1.45
        perimeter_km = round(elongation * 2.0 * np.sqrt(3.14159 * max(0.001, area_sq_km)), 2)

    turb_val = turbidity_ntu if turbidity_ntu is not None else (45.0 if elongation > 4.0 else 18.0)

    if BODY_TYPE_MODEL_PATH.exists() and BODY_TYPE_SCALER_PATH.exists() and BODY_TYPE_ENCODER_PATH.exists():
        if _bt_model is None:
            _bt_model = joblib.load(BODY_TYPE_MODEL_PATH)
            _bt_scaler = joblib.load(BODY_TYPE_SCALER_PATH)
            _bt_encoder = joblib.load(BODY_TYPE_ENCODER_PATH)

        feats = np.array([[area_sq_km, perimeter_km, elongation, occ, season, ndwi_val, turb_val]])
        feats_scaled = _bt_scaler.transform(feats)
        pred_enc = _bt_model.predict(feats_scaled)[0]
        pred_label = _bt_encoder.inverse_transform([pred_enc])[0]
        proba = _bt_model.predict_proba(feats_scaled)[0]
        confidence = float(np.max(proba))
        type_probs = {
            _bt_encoder.inverse_transform([i])[0]: float(p)
            for i, p in enumerate(proba)
        }
        return {
            "predicted_water_body_type": pred_label,
            "confidence": round(confidence, 4),
            "type_probabilities": type_probs,
            "model_used": "RandomForest_Task1",
        }

    # Heuristic fallback if model not loaded
    if is_artificial:
        predicted_type = "reservoir"
        confidence = 0.90
    elif area_sq_km < 0.05:
        predicted_type = "pond"
        confidence = 0.94
    elif occ < 65.0 or season < 6:
        predicted_type = "wetland"
        confidence = 0.88
    elif elongation > 4.0:
        predicted_type = "river"
        confidence = 0.95
    else:
        predicted_type = "lake"
        confidence = 0.92

    type_probabilities = {
        "pond": 0.05,
        "lake": 0.05,
        "reservoir": 0.05,
        "wetland": 0.05,
        "river": 0.05,
    }
    type_probabilities[predicted_type] = confidence
    remaining = (1.0 - confidence) / (len(type_probabilities) - 1)
    for k in type_probabilities:
        if k != predicted_type:
            type_probabilities[k] = round(remaining, 3)

    return {
        "predicted_water_body_type": predicted_type,
        "confidence": confidence,
        "type_probabilities": type_probabilities,
        "model_used": "Heuristic_Fallback",
    }



