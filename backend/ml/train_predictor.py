"""
Train the future water body condition predictor.

For each water body with enough historical data,
fits a polynomial regression on NDWI and area over years.
The resulting coefficients are saved so the predictor service
can extrapolate future values without re-training at request time.

Run:
    cd backend
    python ml/train_predictor.py
"""
import pandas as pd
import numpy as np
from pathlib import Path
import joblib
import sys
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).parent.parent))

PROC_DIR = Path(__file__).parent.parent.parent / "data" / "processed"
MODEL_DIR = Path(__file__).parent / "models"
MODEL_DIR.mkdir(exist_ok=True)


def load_data():
    obs_path = PROC_DIR / "temporal_observations.csv"
    if not obs_path.exists():
        raise FileNotFoundError("Run download_data.py and preprocess.py first.")
    obs = pd.read_csv(obs_path)
    obs["observation_year"] = obs["observation_year"].astype(int)
    return obs


def train_per_wb_models(obs: pd.DataFrame) -> dict:
    """
    For each water body, fit polynomial regression models on:
      - NDWI vs year
      - area_sq_km vs year
      - water_quality_score vs year
    Returns a dict: { wb_index -> {ndwi_coeff, area_coeff, qual_coeff, years} }
    """
    models = {}
    wb_groups = obs.groupby("wb_index")
    total = len(wb_groups)
    print(f"  Fitting time-series models for {total} water bodies...")

    for i, (wb_idx, grp) in enumerate(wb_groups):
        grp = grp.sort_values("observation_year").dropna(subset=["ndwi", "area_sq_km"])
        if len(grp) < 2:
            continue

        years = grp["observation_year"].values.astype(float)
        ndwi = grp["ndwi"].values
        area = grp["area_sq_km"].values
        quality = grp["water_quality_score"].fillna(50.0).values

        deg = min(2, len(years) - 1)
        try:
            ndwi_coeff = np.polyfit(years, ndwi, deg).tolist()
            area_coeff = np.polyfit(years, area, deg).tolist()
            qual_coeff = np.polyfit(years, quality, deg).tolist()
        except Exception:
            continue

        models[int(wb_idx)] = {
            "ndwi_coeff": ndwi_coeff,
            "area_coeff": area_coeff,
            "qual_coeff": qual_coeff,
            "min_year": int(years.min()),
            "max_year": int(years.max()),
            "degree": deg,
        }

        if (i + 1) % 500 == 0:
            print(f"    ... {i+1}/{total} done")

    print(f"  ✓ Fitted models for {len(models)} water bodies.")
    return models


if __name__ == "__main__":
    print("\n🌊 Water Body Future Predictor Training")
    print("=" * 50)

    obs = load_data()
    models = train_per_wb_models(obs)

    out_path = MODEL_DIR / "predictor.pkl"
    joblib.dump(models, out_path)
    print(f"\n  ✓ Predictor saved to {out_path}")
    print(f"  Coverage: {len(models)} water bodies with fitted time-series models.")
    print("\n✅ Training complete.")

