"""
Prediction router — predict future water body conditions.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from services.predictor import predict_future
from services.retrieval import get_water_body_by_id
from services.mock_data import get_mock_water_body_detail

router = APIRouter(prefix="/api/predict", tags=["Prediction"])


@router.get("/{wb_id}")
def predict_water_body_future(
    wb_id: int,
    years_ahead: int = Query(5, ge=1, le=15, description="How many years into the future to predict"),
    db: Session = Depends(get_db),
):
    """
    Predict future NDWI, area, and water quality status for a water body.
    Returns predictions for each year from (current_year + 1) to (current_year + years_ahead).
    """
    try:
        wb = get_water_body_by_id(db, wb_id)
        if not wb:
            detail = get_mock_water_body_detail(wb_id)
            return {"water_body_id": wb_id, "predictions": detail.predictions[:years_ahead]}

        from datetime import datetime
        current_year = datetime.now().year
        target_years = list(range(current_year + 1, current_year + years_ahead + 1))

        predictions = predict_future(db, wb_id, target_years)
        if not predictions:
            raise HTTPException(
                status_code=422,
                detail="Not enough historical data to generate predictions (need at least 2 observations)."
            )
        return {"water_body_id": wb_id, "predictions": predictions}
    except Exception as e:
        print(f"INFO: Database unavailable, serving demo predictions: {e}")
        detail = get_mock_water_body_detail(wb_id)
        return {"water_body_id": wb_id, "predictions": detail.predictions[:years_ahead]}


