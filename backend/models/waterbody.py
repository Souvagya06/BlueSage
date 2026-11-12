"""
SQLAlchemy ORM models for water bodies and temporal observations.
"""
from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, Enum as SAEnum,
    ForeignKey, Index, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
import enum
from database import Base


class WaterBodyType(str, enum.Enum):
    lake = "lake"
    pond = "pond"
    reservoir = "reservoir"
    river = "river"
    wetland = "wetland"
    other = "other"


class WaterQualityStatus(str, enum.Enum):
    excellent = "excellent"
    good = "good"
    fair = "fair"
    poor = "poor"
    critical = "critical"


class WaterBody(Base):
    """
    Master record for each water body.
    Geometry stored as PostGIS POINT (centroid) + POLYGON (outline).
    """
    __tablename__ = "water_bodies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    water_body_type = Column(SAEnum(WaterBodyType), nullable=False, index=True)
    country = Column(String(100), nullable=False, index=True)
    country_code = Column(String(3), index=True)
    state_region = Column(String(150))
    city = Column(String(150), index=True)

    # Spatial — centroid point (EPSG:4326 / WGS84)
    centroid = Column(Geometry("POINT", srid=4326), nullable=False)

    # Polygon outline (nullable — not all sources provide it)
    outline = Column(Geometry("POLYGON", srid=4326), nullable=True)

    # Source metadata
    source_id = Column(String(100), comment="ID from original dataset (e.g. HydroLAKES lake_id)")
    data_source = Column(String(100), nullable=False, comment="e.g. HydroLAKES, USGS, GLWD")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    observations = relationship("TemporalObservation", back_populates="water_body", cascade="all, delete-orphan")
    predictions = relationship("FuturePrediction", back_populates="water_body", cascade="all, delete-orphan")

    # Spatial index (GiST) for fast geographic queries
    __table_args__ = (
        Index("idx_wb_centroid_gist", "centroid", postgresql_using="gist"),
        Index("idx_wb_country_type", "country", "water_body_type"),
    )


class TemporalObservation(Base):
    """
    One row per water body per year of observation.
    Contains NDWI, area, water quality parameters etc.
    """
    __tablename__ = "temporal_observations"

    id = Column(Integer, primary_key=True, index=True)
    water_body_id = Column(Integer, ForeignKey("water_bodies.id", ondelete="CASCADE"), nullable=False)
    observation_year = Column(Integer, nullable=False, index=True)
    observation_date = Column(Date, nullable=True)

    # Core parameters from PPT
    area_sq_km = Column(Float, comment="Water surface area in km²")
    ndwi = Column(Float, comment="Normalized Difference Water Index (-1 to 1)")
    ndwi_min = Column(Float)
    ndwi_max = Column(Float)

    # Water quality indicators
    water_quality_status = Column(SAEnum(WaterQualityStatus), index=True)
    water_quality_score = Column(Float, comment="Composite 0–100 score")
    turbidity_ntu = Column(Float, nullable=True)
    ph = Column(Float, nullable=True)
    dissolved_oxygen_mgl = Column(Float, nullable=True)
    chlorophyll_a_ugl = Column(Float, nullable=True)

    # Remote sensing derived
    water_occurrence_pct = Column(Float, comment="% of time pixel covered by water (JRC GSW)")
    seasonality_months = Column(Integer, comment="Months per year water is present")

    # Source
    data_source = Column(String(100))
    notes = Column(Text, nullable=True)

    water_body = relationship("WaterBody", back_populates="observations")

    __table_args__ = (
        Index("idx_obs_wb_year", "water_body_id", "observation_year"),
        Index("idx_obs_year_ndwi", "observation_year", "ndwi"),
        Index("idx_obs_quality", "water_quality_status"),
    )


class FuturePrediction(Base):
    """
    ML-generated future predictions for a water body.
    """
    __tablename__ = "future_predictions"

    id = Column(Integer, primary_key=True, index=True)
    water_body_id = Column(Integer, ForeignKey("water_bodies.id", ondelete="CASCADE"), nullable=False)
    target_year = Column(Integer, nullable=False, index=True)

    predicted_area_sq_km = Column(Float)
    predicted_ndwi = Column(Float)
    predicted_quality_status = Column(SAEnum(WaterQualityStatus))
    predicted_quality_score = Column(Float)

    model_name = Column(String(100))
    confidence_score = Column(Float, comment="Model confidence 0–1")
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    water_body = relationship("WaterBody", back_populates="predictions")

    __table_args__ = (
        Index("idx_pred_wb_year", "water_body_id", "target_year"),
    )

