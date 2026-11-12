"""
Classification router — classify a water body observation using the ML model.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.classifier import classify_water_body, classify_water_body_type

router = APIRouter(prefix="/api/classify", tags=["Classification"])


class ClassifyTypeRequest(BaseModel):
    area_sq_km: float
    water_occurrence_pct: Optional[float] = 85.0
    seasonality_months: Optional[int] = 10
    perimeter_km: Optional[float] = None
    is_artificial: Optional[bool] = False


class ClassifyRequest(BaseModel):
    ndwi: float
    area_sq_km: float
    water_body_type: str
    water_occurrence_pct: Optional[float] = None
    seasonality_months: Optional[int] = None
    turbidity_ntu: Optional[float] = None
    ph: Optional[float] = None
    dissolved_oxygen_mgl: Optional[float] = None
    chlorophyll_a_ugl: Optional[float] = None


@router.post("/body-type")
def classify_type(req: ClassifyTypeRequest):
    """
    Task 1: Water-body classification.
    Identify whether a water body is a pond, lake, reservoir, wetland, or river
    based on surface area, seasonality, water occurrence, and morphology.
    """
    return classify_water_body_type(
        area_sq_km=req.area_sq_km,
        water_occurrence_pct=req.water_occurrence_pct,
        seasonality_months=req.seasonality_months,
        perimeter_km=req.perimeter_km,
        is_artificial=req.is_artificial,
    )


@router.post("/")
def classify(req: ClassifyRequest):
    """
    Classify a water body's quality status using the trained Random Forest model.
    Returns predicted quality class and confidence scores.
    """
    try:
        result = classify_water_body(
            ndwi=req.ndwi,
            area_sq_km=req.area_sq_km,
            water_occurrence_pct=req.water_occurrence_pct,
            seasonality_months=req.seasonality_months,
            turbidity_ntu=req.turbidity_ntu,
            ph=req.ph,
            dissolved_oxygen_mgl=req.dissolved_oxygen_mgl,
            chlorophyll_a_ugl=req.chlorophyll_a_ugl,
            water_body_type=req.water_body_type,
        )
        return result
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="ML model not yet trained. Run backend/ml/train_classifier.py first."
        )

