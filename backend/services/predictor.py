"""
Future prediction service — predicts NDWI, area, and quality for future years.
Uses a per-water-body time-series model (Linear Regression as default).
"""
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models.waterbody import TemporalObservation, WaterQualityStatus

PREDICTOR_PATH = Path(__file__).parent.parent / "ml" / "models" / "predictor.pkl"

_global_predictor = None


def _load_predictor():
    global _global_predictor
    if _global_predictor is None and PREDICTOR_PATH.exists():
        _global_predictor = joblib.load(PREDICTOR_PATH)
    return _global_predictor


def _quality_score_to_status(score: float) -> str:
    if score >= 80:
        return "excellent"
    elif score >= 60:
        return "good"
    elif score >= 40:
        return "fair"
    elif score >= 20:
        return "poor"
    return "critical"


def predict_future(
    db: Session,
    water_body_id: int,
    target_years: List[int],
) -> List[Dict[str, Any]]:
    """
    For a given water body, fetch its historical observations and
    extrapolate NDWI, area, and quality score for each target year.
    Uses polynomial regression on historical time series.
    """
    obs = (
        db.query(TemporalObservation)
        .filter(TemporalObservation.water_body_id == water_body_id)
        .order_by(TemporalObservation.observation_year)
        .all()
    )

    if len(obs) < 2:
        return []

    years = np.array([o.observation_year for o in obs], dtype=float)
    ndwi_vals = np.array([o.ndwi if o.ndwi is not None else 0.0 for o in obs])
    area_vals = np.array([o.area_sq_km if o.area_sq_km is not None else 0.0 for o in obs])
    quality_vals = np.array([o.water_quality_score if o.water_quality_score is not None else 50.0 for o in obs])

    # Fit polynomial degree 2 for each metric
    ndwi_coeff = np.polyfit(years, ndwi_vals, min(2, len(years) - 1))
    area_coeff = np.polyfit(years, area_vals, min(2, len(years) - 1))
    qual_coeff = np.polyfit(years, quality_vals, min(2, len(years) - 1))

    ndwi_poly = np.poly1d(ndwi_coeff)
    area_poly = np.poly1d(area_coeff)
    qual_poly = np.poly1d(qual_coeff)

    baseline_area = area_vals[-1] if len(area_vals) > 0 and area_vals[-1] > 0 else 1.0

    predictions = []
    for yr in target_years:
        pred_ndwi = float(np.clip(ndwi_poly(yr), -1.0, 1.0))
        pred_area = float(max(0.0, area_poly(yr)))
        pred_quality = float(np.clip(qual_poly(yr), 0.0, 100.0))
        pred_status = _quality_score_to_status(pred_quality)

        # Categorize change trend: stable / shrink / expand / disappear
        if pred_area <= 0.05 * baseline_area or pred_area <= 0.001:
            trend = "disappear"
        elif pred_area < 0.90 * baseline_area:
            trend = "shrink"
        elif pred_area > 1.10 * baseline_area:
            trend = "expand"
        else:
            trend = "stable"

        predictions.append({
            "water_body_id": water_body_id,
            "target_year": yr,
            "predicted_ndwi": round(pred_ndwi, 4),
            "predicted_area_sq_km": round(pred_area, 4),
            "predicted_quality_score": round(pred_quality, 2),
            "predicted_quality_status": pred_status,
            "change_trend": trend,
            "model_name": "polynomial_regression_v1",
            "confidence_score": max(0.3, min(0.95, 1.0 - 0.05 * (yr - max(years)))),
        })

    return predictions

