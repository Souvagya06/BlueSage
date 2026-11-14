"""
Pydantic schemas for WaterBody, TemporalObservation, and FuturePrediction.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from models.waterbody import WaterBodyType, WaterQualityStatus


# ─── Observation Schemas ───────────────────────────────────────────────────────

class ObservationBase(BaseModel):
    observation_year: int
    observation_date: Optional[date] = None
    area_sq_km: Optional[float] = None
    ndwi: Optional[float] = None
    ndwi_min: Optional[float] = None
    ndwi_max: Optional[float] = None
    water_quality_status: Optional[WaterQualityStatus] = None
    water_quality_score: Optional[float] = None
    turbidity_ntu: Optional[float] = None
    ph: Optional[float] = None
    dissolved_oxygen_mgl: Optional[float] = None
    chlorophyll_a_ugl: Optional[float] = None
    water_occurrence_pct: Optional[float] = None
    seasonality_months: Optional[int] = None
    data_source: Optional[str] = None
    notes: Optional[str] = None


class ObservationOut(ObservationBase):
    id: int
    water_body_id: int

    class Config:
        from_attributes = True
        protected_namespaces = ()


# ─── Prediction Schemas ────────────────────────────────────────────────────────

class PredictionOut(BaseModel):
    id: int
    water_body_id: int
    target_year: int
    predicted_area_sq_km: Optional[float]
    predicted_ndwi: Optional[float]
    predicted_quality_status: Optional[WaterQualityStatus]
    predicted_quality_score: Optional[float]
    change_trend: Optional[str] = "stable"  # "stable", "shrink", "expand", "disappear"
    model_name: Optional[str]
    confidence_score: Optional[float]
    generated_at: Optional[datetime]

    class Config:
        from_attributes = True
        protected_namespaces = ()


# ─── Water Body Schemas ────────────────────────────────────────────────────────

class WaterBodyBase(BaseModel):
    name: str
    water_body_type: WaterBodyType
    country: str
    country_code: Optional[str] = None
    state_region: Optional[str] = None
    city: Optional[str] = None
    data_source: str
    source_id: Optional[str] = None


class WaterBodyOut(WaterBodyBase):
    id: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    area_sq_km: Optional[float] = None
    perimeter_km: Optional[float] = None
    elongation_ratio: Optional[float] = None
    spatial_grid_index: Optional[str] = None
    created_at: Optional[datetime] = None
    observations: List[ObservationOut] = []

    class Config:
        from_attributes = True
        protected_namespaces = ()


class WaterBodyDetail(WaterBodyOut):
    observations: List[ObservationOut] = []
    predictions: List[PredictionOut] = []


# ─── Search / Filter Schemas ───────────────────────────────────────────────────

class BoundingBox(BaseModel):
    min_lat: float = Field(..., ge=-90, le=90)
    max_lat: float = Field(..., ge=-90, le=90)
    min_lon: float = Field(..., ge=-180, le=180)
    max_lon: float = Field(..., ge=-180, le=180)


class WaterBodySearchParams(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None
    water_body_type: Optional[WaterBodyType] = None
    year: Optional[int] = None
    min_ndwi: Optional[float] = None
    max_ndwi: Optional[float] = None
    quality_status: Optional[WaterQualityStatus] = None
    bbox: Optional[BoundingBox] = None
    limit: int = Field(100, le=500)
    offset: int = 0

