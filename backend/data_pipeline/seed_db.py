"""
Database seeding script.
Reads processed CSVs and inserts real water body + temporal observation data
into the PostgreSQL + PostGIS database.

Run after preprocess.py:
    python data_pipeline/seed_db.py
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
from models.waterbody import WaterBody, TemporalObservation, WaterBodyType, WaterQualityStatus
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy import text
import requests
import time

PROC_DIR = Path(__file__).parent.parent.parent / "data" / "processed"


def geocode_city_nominatim(country: str, name: str) -> str:
    """Reverse-geocode approximate city using Nominatim (free, no key)."""
    url = "https://nominatim.openstreetmap.org/reverse"
    # We only use this for enrichment; most records will have country already
    return None


def enrich_city(lat: float, lon: float) -> dict:
    """
    Use Nominatim reverse geocoding to get city/state for a lat/lon.
    Free and open — no API key needed.
    Rate-limited to 1 req/sec per Nominatim policy.
    """
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {"lat": lat, "lon": lon, "format": "json", "zoom": 10}
    headers = {"User-Agent": "WaterBodyResearchProject/1.0 (academic@research.edu)"}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        addr = data.get("address", {})
        return {
            "city": addr.get("city") or addr.get("town") or addr.get("village") or addr.get("county", ""),
            "state_region": addr.get("state", ""),
            "country_code": addr.get("country_code", "").upper(),
        }
    except Exception:
        return {"city": "", "state_region": "", "country_code": ""}


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("  ✓ Database tables created / verified.")


def seed_water_bodies(db: Session, wb_df: pd.DataFrame, enrich_geocode: bool = False) -> dict:
    """Insert water body master records. Returns mapping wb_index -> DB id."""
    print(f"  Inserting {len(wb_df)} water body records...")
    index_to_id = {}

    # Create PostGIS indexes after bulk insert
    for idx, row in wb_df.iterrows():
        lat = float(row.get("latitude", 0))
        lon = float(row.get("longitude", 0))
        if lat == 0 and lon == 0:
            continue

        # Reverse geocode a sample (Nominatim has rate limit — only do first 200)
        city = ""
        state_region = ""
        country_code = str(row.get("country_code", "") or "")
        if enrich_geocode and idx < 200:
            geo = enrich_city(lat, lon)
            city = geo["city"]
            state_region = geo["state_region"]
            if not country_code:
                country_code = geo["country_code"]
            time.sleep(1.1)  # Nominatim rate limit: 1 req/sec

        wb_type_str = str(row.get("water_body_type", "other"))
        if wb_type_str not in [t.value for t in WaterBodyType]:
            wb_type_str = "other"

        point_geom = from_shape(Point(lon, lat), srid=4326)

        wb = WaterBody(
            name=str(row.get("name", "Unnamed"))[:255],
            water_body_type=WaterBodyType(wb_type_str),
            country=str(row.get("country", "Unknown"))[:100],
            country_code=country_code[:3] if country_code else None,
            state_region=state_region[:150] if state_region else None,
            city=city[:150] if city else None,
            centroid=point_geom,
            source_id=str(row.get("source_id", ""))[:100],
            data_source=str(row.get("data_source", "HydroLAKES_v1.0"))[:100],
        )
        db.add(wb)
        db.flush()  # get the generated ID
        index_to_id[idx] = wb.id

        if idx % 500 == 0:
            db.commit()
            print(f"    ... {idx} water bodies inserted")

    db.commit()
    print(f"  ✓ {len(index_to_id)} water bodies inserted.")
    return index_to_id


def seed_observations(db: Session, obs_df: pd.DataFrame, index_to_id: dict):
    """Insert temporal observation records."""
    print(f"  Inserting {len(obs_df)} temporal observation records...")

    batch = []
    for i, row in obs_df.iterrows():
        wb_idx = int(row["wb_index"])
        wb_id = index_to_id.get(wb_idx)
        if wb_id is None:
            continue

        status_str = str(row.get("water_quality_status", "fair"))
        if status_str not in [s.value for s in WaterQualityStatus]:
            status_str = "fair"

        obs = TemporalObservation(
            water_body_id=wb_id,
            observation_year=int(row["observation_year"]),
            area_sq_km=float(row["area_sq_km"]) if pd.notna(row.get("area_sq_km")) else None,
            ndwi=float(row["ndwi"]) if pd.notna(row.get("ndwi")) else None,
            ndwi_min=float(row["ndwi_min"]) if pd.notna(row.get("ndwi_min")) else None,
            ndwi_max=float(row["ndwi_max"]) if pd.notna(row.get("ndwi_max")) else None,
            water_quality_status=WaterQualityStatus(status_str),
            water_quality_score=float(row["water_quality_score"]) if pd.notna(row.get("water_quality_score")) else None,
            ph=float(row["ph"]) if pd.notna(row.get("ph")) else None,
            dissolved_oxygen_mgl=float(row["dissolved_oxygen_mgl"]) if pd.notna(row.get("dissolved_oxygen_mgl")) else None,
            turbidity_ntu=float(row["turbidity_ntu"]) if pd.notna(row.get("turbidity_ntu")) else None,
            chlorophyll_a_ugl=float(row["chlorophyll_a_ugl"]) if pd.notna(row.get("chlorophyll_a_ugl")) else None,
            water_occurrence_pct=float(row["water_occurrence_pct"]) if pd.notna(row.get("water_occurrence_pct")) else None,
            seasonality_months=int(row["seasonality_months"]) if pd.notna(row.get("seasonality_months")) else None,
            data_source=str(row.get("data_source", "HydroLAKES_v1.0")),
        )
        batch.append(obs)

        if len(batch) >= 1000:
            db.bulk_save_objects(batch)
            db.commit()
            batch = []
            print(f"    ... {i} observations inserted")

    if batch:
        db.bulk_save_objects(batch)
        db.commit()

    print(f"  ✓ Temporal observations inserted.")


def create_additional_indexes(db: Session):
    """Create extra indexes for performance (beyond SQLAlchemy model defaults)."""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_wb_name_trgm ON water_bodies USING gin(name gin_trgm_ops)",
        "CREATE INDEX IF NOT EXISTS idx_obs_ndwi_btree ON temporal_observations (ndwi)",
        "CREATE INDEX IF NOT EXISTS idx_obs_area_btree ON temporal_observations (area_sq_km)",
        "CREATE INDEX IF NOT EXISTS idx_obs_quality_score ON temporal_observations (water_quality_score)",
    ]
    for sql in indexes:
        try:
            db.execute(text(sql))
        except Exception as e:
            print(f"    ! Index creation skipped (may need pg_trgm extension): {e}")
    db.commit()
    print("  ✓ Additional indexes created.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Seed the water body database with real data.")
    parser.add_argument("--geocode", action="store_true", help="Enrich with Nominatim reverse geocoding (slow, rate-limited)")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of water bodies to insert (for testing)")
    args = parser.parse_args()

    print("\n🌊 Water Body Database Seeding")
    print("=" * 50)

    wb_path = PROC_DIR / "water_bodies.csv"
    obs_path = PROC_DIR / "temporal_observations.csv"

    if not wb_path.exists():
        print("ERROR: data/processed/water_bodies.csv not found.")
        print("Run: python data_pipeline/download_data.py && python data_pipeline/preprocess.py")
        sys.exit(1)

    wb_df = pd.read_csv(wb_path, index_col="wb_index")
    obs_df = pd.read_csv(obs_path)

    if args.limit:
        wb_df = wb_df.head(args.limit)
        obs_df = obs_df[obs_df["wb_index"].isin(wb_df.index)]
        print(f"  Limited to {args.limit} water bodies for testing.")

    print(f"\n  Water bodies: {len(wb_df)}")
    print(f"  Observations: {len(obs_df)}")

    db = SessionLocal()
    try:
        print("\n[1/4] Creating database tables...")
        create_tables()

        print("\n[2/4] Seeding water bodies...")
        index_to_id = seed_water_bodies(db, wb_df, enrich_geocode=args.geocode)

        print("\n[3/4] Seeding temporal observations...")
        seed_observations(db, obs_df, index_to_id)

        print("\n[4/4] Creating performance indexes...")
        create_additional_indexes(db)

        # Count
        wb_count = db.execute(text("SELECT COUNT(*) FROM water_bodies")).scalar()
        obs_count = db.execute(text("SELECT COUNT(*) FROM temporal_observations")).scalar()
        print(f"\n✅ Database seeded successfully!")
        print(f"   Water bodies: {wb_count}")
        print(f"   Observations: {obs_count}")

    finally:
        db.close()

