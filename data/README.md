# Data Directory

## Real Data Sources

This project uses **100% real, open-source data** — no synthetic data.

### Source 1: HydroLAKES v1.0
- **What:** Global lake and reservoir polygons with area, volume, coordinates
- **Coverage:** ~1.4 million lakes worldwide
- **Download:** https://www.hydrosheds.org/products/hydrolakes
- **License:** CC BY 4.0
- **File produced:** `raw/hydrolakes_sample.csv`

### Source 2: USGS Water Quality Portal (NWIS)
- **What:** Lake/reservoir water quality monitoring data (pH, dissolved oxygen, turbidity, chlorophyll-a)
- **Coverage:** USA lake monitoring stations, 2014–2024
- **API:** https://www.waterqualitydata.us/ (free, no key)
- **File produced:** `raw/usgs_water_quality.csv`

### Source 3: JRC Global Surface Water
- **What:** Monthly water occurrence and seasonality derived from Landsat imagery, 1984–2021
- **Coverage:** Global
- **Download:** https://global-surface-water.appspot.com/download
- **License:** Free for research/educational use
- **File produced:** `raw/jrc_gsw_statistics.csv`

### Source 4: OpenStreetMap Nominatim
- **What:** City reverse geocoding (city/country lookup for coordinates)
- **API:** https://nominatim.openstreetmap.org (free, rate-limited to 1 req/sec)
- **License:** ODbL

## Processed Files (auto-generated)

| File | Description |
|---|---|
| `processed/water_bodies.csv` | Cleaned master list of water bodies |
| `processed/temporal_observations.csv` | 10-year temporal observations per water body |

Run `python backend/data_pipeline/download_data.py` then `python backend/data_pipeline/preprocess.py` to generate.

