"""
Water body retrieval service — handles indexed spatial and attribute queries.
"""
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from geoalchemy2.functions import ST_DWithin, ST_GeomFromText, ST_Distance, ST_MakeEnvelope
from models.waterbody import WaterBody, TemporalObservation
from schemas.waterbody import WaterBodySearchParams
from typing import List, Optional


def search_water_bodies(db: Session, params: WaterBodySearchParams) -> List[WaterBody]:
    """
    Multi-filter query using DB indexes:
      - GiST spatial index for bounding-box / proximity queries
      - B-Tree indexes on country, type, year, ndwi
      - Hash index on city (via B-Tree in PG 13+)
    """
    query = db.query(WaterBody)

    # ── Spatial bounding-box filter (uses GiST index) ──
    if params.bbox:
        bbox = params.bbox
        query = query.filter(
            func.ST_Within(
                WaterBody.centroid,
                func.ST_MakeEnvelope(
                    bbox.min_lon, bbox.min_lat,
                    bbox.max_lon, bbox.max_lat,
                    4326
                )
            )
        )

    # ── Attribute filters (use B-Tree indexes) ──
    if params.country:
        query = query.filter(WaterBody.country.ilike(f"%{params.country}%"))
    if params.city:
        query = query.filter(WaterBody.city.ilike(f"%{params.city}%"))
    if params.water_body_type:
        query = query.filter(WaterBody.water_body_type == params.water_body_type)

    # ── Join to observations for year / NDWI / quality filters ──
    if any([params.year, params.min_ndwi is not None, params.max_ndwi is not None, params.quality_status]):
        query = query.join(TemporalObservation, WaterBody.id == TemporalObservation.water_body_id)
        if params.year:
            query = query.filter(TemporalObservation.observation_year == params.year)
        if params.min_ndwi is not None:
            query = query.filter(TemporalObservation.ndwi >= params.min_ndwi)
        if params.max_ndwi is not None:
            query = query.filter(TemporalObservation.ndwi <= params.max_ndwi)
        if params.quality_status:
            query = query.filter(TemporalObservation.water_quality_status == params.quality_status)

    return query.distinct().offset(params.offset).limit(params.limit).all()


def get_water_body_by_id(db: Session, wb_id: int) -> Optional[WaterBody]:
    return db.query(WaterBody).filter(WaterBody.id == wb_id).first()


def get_water_bodies_near_point(
    db: Session, lat: float, lon: float, radius_km: float = 50, limit: int = 100
) -> List[WaterBody]:
    """
    Find all water bodies within `radius_km` of a lat/lon point.
    Uses the GiST spatial index on the centroid column.
    radius_km is converted to degrees approximately for ST_DWithin.
    """
    # ST_DWithin with geography type for accurate km-based distance
    point_wkt = f"SRID=4326;POINT({lon} {lat})"
    return (
        db.query(WaterBody)
        .filter(
            func.ST_DWithin(
                func.ST_Transform(WaterBody.centroid, 4326),
                func.ST_GeomFromEWKT(point_wkt),
                radius_km * 1000,  # metres when using geography
                True  # use_spheroid
            )
        )
        .limit(limit)
        .all()
    )


def get_query_performance_stats(db: Session, query_sql: str) -> dict:
    """Run EXPLAIN ANALYZE on a query and return stats."""
    result = db.execute(text(f"EXPLAIN ANALYZE {query_sql}"))
    plan = "\n".join([row[0] for row in result])
    return {"explain_analyze": plan}

