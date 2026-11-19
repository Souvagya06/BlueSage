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
from fastapi.responses import FileResponse, Response
import io
import re
import pandas as pd
import numpy as np
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
def export_indexed_csv(
    water_body_type: Optional[str] = Query(
        None,
        description="Filter indexed dataset by water body type: wetland, pond, river, lake, reservoir",
    ),
    city: Optional[str] = Query(None, description="Filter dataset by city / location name"),
    country: Optional[str] = Query(None, description="Filter dataset by country name"),
    lat: Optional[float] = Query(None, description="Center latitude for proximity radius filter"),
    lon: Optional[float] = Query(None, description="Center longitude for proximity radius filter"),
    radius_km: Optional[float] = Query(None, description="Search radius in kilometers around (lat, lon)"),
):
    """
    Download the indexed temporal dataset as a CSV file.
    Supports filtering by:
    - Location: city, country, or coordinates (lat, lon, radius_km)
    - Specific water body types (wetland, pond, river, lake, reservoir).
    """
    rad = float(radius_km) if isinstance(radius_km, (int, float)) else 200.0
    lat_val = float(lat) if isinstance(lat, (int, float)) else None
    lon_val = float(lon) if isinstance(lon, (int, float)) else None
    city_val = str(city).strip() if city and isinstance(city, str) else None
    country_val = str(country).strip() if country and isinstance(country, str) else None
    type_val = str(water_body_type).strip().lower() if water_body_type and isinstance(water_body_type, str) else None

    proc_dir = Path(__file__).resolve().parent.parent.parent / "data" / "processed"
    master_csv = proc_dir / "indexed_waterbody_dataset.csv"
    if not master_csv.exists():
        from data_pipeline.export_indexed_dataset import generate_indexed_dataset
        generate_indexed_dataset()

    # If spatial or location filtering is requested, generate dynamic location CSV
    if (lat_val is not None and lon_val is not None) or city_val or country_val:
        df = pd.read_csv(master_csv)

        if lat_val is not None and lon_val is not None:
            # Haversine distance in km
            dlat = np.radians(df["latitude"] - lat_val)
            dlon = np.radians(df["longitude"] - lon_val)
            a = np.sin(dlat / 2.0)**2 + np.cos(np.radians(lat_val)) * np.cos(np.radians(df["latitude"])) * np.sin(dlon / 2.0)**2
            dists = 2.0 * 6371.0 * np.arcsin(np.sqrt(a))
            df["distance_km"] = np.round(dists, 2)

            filtered = df[df["distance_km"] <= rad]
            if filtered.empty:
                # Fallback to nearest 15 water bodies
                filtered = df.sort_values("distance_km").head(165)  # 15 water bodies * 11 years
        else:
            filtered = df

        if city_val:
            if lat_val is None or lon_val is None:
                filtered = filtered[
                    filtered["city"].str.contains(city_val, case=False, na=False) |
                    filtered["water_body_name"].str.contains(city_val, case=False, na=False)
                ]

        if country_val:
            filtered = filtered[filtered["country"].str.contains(country_val, case=False, na=False)]

        if type_val:
            filtered = filtered[filtered["target_task1_body_type"].str.lower() == type_val]

        if filtered.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No indexed water bodies found matching location criteria.",
            )

        # Generate CSV stream
        loc_label = city_val or (f"lat{lat_val:.2f}_lon{lon_val:.2f}" if lat_val is not None else "location")
        safe_loc = re.sub(r"[^a-zA-Z0-9_\-]+", "_", loc_label).strip("_").lower()
        filename = f"indexed_waterbodies_{safe_loc}.csv"

        stream = io.StringIO()
        filtered.to_csv(stream, index=False)
        return Response(
            content=stream.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    # Standard static exports (all or by type)
    if water_body_type:
        type_clean = water_body_type.strip().lower()
        type_csv = proc_dir / f"indexed_dataset_{type_clean}.csv"
        
        # If specific type CSV does not exist, generate on the fly from master
        if not type_csv.exists():
            df = pd.read_csv(master_csv)
            filtered = df[df["target_task1_body_type"].str.lower() == type_clean]
            if filtered.empty:
                raise HTTPException(
                    status_code=404,
                    detail=f"No records found for water body type: '{water_body_type}'. Available: wetland, pond, river, lake, reservoir.",
                )
            filtered.to_csv(type_csv, index=False)

        return FileResponse(
            path=str(type_csv),
            filename=f"indexed_waterbody_dataset_{type_clean}.csv",
            media_type="text/csv",
        )

    return FileResponse(
        path=str(master_csv),
        filename="indexed_waterbody_dataset.csv",
        media_type="text/csv",
    )


@router.get("/indexed-datasets")
def list_indexed_datasets():
    """
    Returns metadata and statistics for all available indexed dataset partitions.
    """
    proc_dir = Path(__file__).resolve().parent.parent.parent / "data" / "processed"
    master_csv = proc_dir / "indexed_waterbody_dataset.csv"
    if not master_csv.exists():
        from data_pipeline.export_indexed_dataset import generate_indexed_dataset
        generate_indexed_dataset()

    import pandas as pd
    df = pd.read_csv(master_csv)
    counts = dict(df["target_task1_body_type"].str.lower().value_counts())

    types_meta = [
        {"type": "all", "label": "Complete Dataset (All Types)", "records": len(df), "filename": "indexed_waterbody_dataset.csv"},
        {"type": "wetland", "label": "Wetlands Only", "records": counts.get("wetland", 0), "filename": "indexed_dataset_wetland.csv"},
        {"type": "pond", "label": "Ponds Only", "records": counts.get("pond", 0), "filename": "indexed_dataset_pond.csv"},
        {"type": "river", "label": "Rivers Only", "records": counts.get("river", 0), "filename": "indexed_dataset_river.csv"},
        {"type": "lake", "label": "Lakes Only", "records": counts.get("lake", 0), "filename": "indexed_dataset_lake.csv"},
        {"type": "reservoir", "label": "Reservoirs Only", "records": counts.get("reservoir", 0), "filename": "indexed_dataset_reservoir.csv"},
    ]

    return {
        "total_records": len(df),
        "total_water_bodies": df["wb_index"].nunique() if "wb_index" in df.columns else None,
        "years": "2014-2024",
        "partitions": types_meta,
    }



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
    limit: int = Query(300, le=500),
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

