"""
Routers for water body CRUD and search endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from geoalchemy2.functions import ST_AsGeoJSON, ST_X, ST_Y
from sqlalchemy import func
import json

from pathlib import Path
from fastapi.responses import FileResponse
from database import get_db
from models.waterbody import WaterBody, TemporalObservation
from schemas.waterbody import (
    WaterBodyOut, WaterBodyDetail, ObservationOut,
    WaterBodySearchParams, BoundingBox
)
from services.retrieval import search_water_bodies, get_water_body_by_id, get_water_bodies_near_point
from services.mock_data import (
    get_mock_water_bodies,
    get_mock_water_bodies_near,
    get_mock_water_body_detail,
)

router = APIRouter(prefix="/api/waterbodies", tags=["Water Bodies"])


@router.get("/export-csv")
def export_indexed_csv():
    """
    Download the entire indexed temporal dataset as a CSV file.
    """
    csv_path = Path(__file__).resolve().parent.parent.parent / "data" / "processed" / "indexed_waterbody_dataset.csv"
    if not csv_path.exists():
        from data_pipeline.export_indexed_dataset import generate_indexed_dataset
        generate_indexed_dataset()

    return FileResponse(
        path=str(csv_path),
        filename="indexed_waterbody_dataset.csv",
        media_type="text/csv",
    )



def _enrich_with_coords(db: Session, wb: WaterBody) -> dict:
    """Add lat/lon extracted from PostGIS geometry."""
    lon = db.scalar(func.ST_X(wb.centroid))
    lat = db.scalar(func.ST_Y(wb.centroid))
    d = {c.name: getattr(wb, c.name) for c in wb.__table__.columns if c.name != "centroid" and c.name != "outline"}
    d["latitude"] = lat
    d["longitude"] = lon
    return d


@router.get("/", response_model=List[WaterBodyOut])
def list_water_bodies(
    country: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    water_body_type: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    min_ndwi: Optional[float] = Query(None),
    max_ndwi: Optional[float] = Query(None),
    quality_status: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    """List / search water bodies with optional filters."""
    try:
        params = WaterBodySearchParams(
            country=country, city=city, water_body_type=water_body_type,
            year=year, min_ndwi=min_ndwi, max_ndwi=max_ndwi,
            quality_status=quality_status, limit=limit, offset=offset,
        )
        wbs = search_water_bodies(db, params)
        result = []
        for wb in wbs:
            d = _enrich_with_coords(db, wb)
            result.append(WaterBodyOut(**d))
        return result
    except Exception as e:
        print(f"INFO: Database unavailable, serving demo water bodies fallback: {e}")
        return get_mock_water_bodies(limit=limit)


@router.get("/near", response_model=List[WaterBodyOut])
def water_bodies_near(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    radius_km: float = Query(200, le=500, description="Search radius in km"),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    """Find water bodies within a radius of a geographic point."""
    try:
        wbs = get_water_bodies_near_point(db, lat, lon, radius_km, limit)
        result = []
        for wb in wbs:
            d = _enrich_with_coords(db, wb)
            result.append(WaterBodyOut(**d))
        return result
    except Exception as e:
        print(f"INFO: Database unavailable, serving demo nearby water bodies: {e}")
        return get_mock_water_bodies_near(lat, lon, radius_km, limit)


@router.get("/bbox", response_model=List[WaterBodyOut])
def water_bodies_in_bbox(
    min_lat: float = Query(...), max_lat: float = Query(...),
    min_lon: float = Query(...), max_lon: float = Query(...),
    limit: int = Query(200, le=500),
    db: Session = Depends(get_db),
):
    """Get all water bodies inside a geographic bounding box."""
    try:
        params = WaterBodySearchParams(
            bbox=BoundingBox(min_lat=min_lat, max_lat=max_lat, min_lon=min_lon, max_lon=max_lon),
            limit=limit,
        )
        wbs = search_water_bodies(db, params)
        result = []
        for wb in wbs:
            d = _enrich_with_coords(db, wb)
            result.append(WaterBodyOut(**d))
        return result
    except Exception as e:
        print(f"INFO: Database unavailable, serving demo bbox water bodies: {e}")
        return get_mock_water_bodies(limit=limit)


@router.get("/{wb_id}", response_model=WaterBodyDetail)
def get_water_body(wb_id: int, db: Session = Depends(get_db)):
    """Get full detail of a water body including all observations and predictions."""
    try:
        wb = get_water_body_by_id(db, wb_id)
        if not wb:
            return get_mock_water_body_detail(wb_id)
        d = _enrich_with_coords(db, wb)
        d["observations"] = wb.observations
        d["predictions"] = wb.predictions
        return WaterBodyDetail(**d)
    except Exception as e:
        print(f"INFO: Database unavailable, serving demo water body detail: {e}")
        return get_mock_water_body_detail(wb_id)


@router.get("/{wb_id}/observations", response_model=List[ObservationOut])
def get_observations(
    wb_id: int,
    start_year: Optional[int] = Query(None),
    end_year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """Get temporal observations for a water body, optionally filtered by year range."""
    try:
        wb = get_water_body_by_id(db, wb_id)
        if not wb:
            raise HTTPException(status_code=404, detail="Water body not found")
        q = db.query(TemporalObservation).filter(TemporalObservation.water_body_id == wb_id)
        if start_year:
            q = q.filter(TemporalObservation.observation_year >= start_year)
        if end_year:
            q = q.filter(TemporalObservation.observation_year <= end_year)
        return q.order_by(TemporalObservation.observation_year).all()
    except Exception as e:
        print(f"INFO: Database unavailable, serving demo observations: {e}")
        detail = get_mock_water_body_detail(wb_id)
        return detail.observations

