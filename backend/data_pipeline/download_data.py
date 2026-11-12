"""
Real data download pipeline for the Temporal Water-Body Dataset project.

Data Sources Used (all open/public):
  1. HydroLAKES v1.0 — Global lake/reservoir polygons with area, volume, coordinates
     URL: https://www.hydrosheds.org/products/hydrolakes
     License: CC BY 4.0

  2. JRC Global Surface Water (GSW) — Yearly water occurrence & seasonality (1984–2021)
     URL: https://global-surface-water.appspot.com/download
     License: free for research/educational use

  3. USGS National Water Information System (NWIS) — Lake water quality monitoring
     URL: https://waterqualitydata.us/ (REST API, free)

  4. OpenStreetMap Nominatim — Reverse geocoding (city/country lookup), free

This script downloads the CSV exports from these sources.
Run: python data_pipeline/download_data.py
"""
import requests
import os
import zipfile
import sys
from pathlib import Path

RAW_DIR = Path(__file__).parent.parent.parent / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)


def download_file(url: str, dest: Path, label: str):
    if dest.exists():
        print(f"  ✓ {label} already downloaded — skipping.")
        return
    print(f"  ↓ Downloading {label} ...")
    headers = {"User-Agent": "WaterBodyResearchProject/1.0 (academic@research.edu)"}
    with requests.get(url, stream=True, headers=headers, timeout=120) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        downloaded = 0
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=65536):
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded * 100 // total
                    print(f"\r    {pct}%", end="", flush=True)
    print(f"\n  ✓ Saved: {dest}")


def download_usgs_water_quality(state_codes: list = None):
    """
    Download water quality data from the USGS Water Quality Portal (REST API).
    Free, no API key needed.
    Returns lake/reservoir monitoring data for all US states by default.
    """
    if state_codes is None:
        # Major states with significant lake data
        state_codes = ["WI", "MN", "MI", "FL", "NY", "CA", "OR", "WA", "TX", "CO"]

    dest = RAW_DIR / "usgs_water_quality.csv"
    if dest.exists():
        print("  ✓ USGS water quality data already downloaded — skipping.")
        return

    print("  ↓ Downloading USGS Water Quality Portal data ...")
    url = "https://www.waterqualitydata.us/data/Result/search"
    params = {
        "statecode": ";".join(f"US:{s}" for s in state_codes),
        "characteristicName": "pH;Dissolved oxygen (DO);Turbidity;Chlorophyll a",
        "siteType": "Lake, Reservoir, Impoundment",
        "startDateLo": "01-01-2014",
        "startDateHi": "12-31-2024",
        "mimeType": "csv",
        "zip": "no",
        "dataProfile": "resultPhysChem",
    }
    headers = {"User-Agent": "WaterBodyResearchProject/1.0"}
    with requests.get(url, params=params, stream=True, headers=headers, timeout=300) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=65536):
                f.write(chunk)
    print(f"  ✓ Saved: {dest}")


def download_hydrolakes_sample():
    """
    HydroLAKES full dataset requires registration.
    We use the publicly available HydroLAKES Polaris REST endpoint
    for a representative global sample.
    """
    dest = RAW_DIR / "hydrolakes_sample.csv"
    if dest.exists():
        print("  ✓ HydroLAKES sample already downloaded — skipping.")
        return

    print("  ↓ Downloading HydroLAKES global sample via REST ...")
    # Using the HydroSHEDS REST service (ArcGIS)
    url = (
        "https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/"
        "HydroLakes_polys_v10/FeatureServer/0/query"
    )
    params = {
        "where": "Lake_area > 1",   # lakes > 1 km²
        "outFields": "Hylak_id,Lake_name,Country,Continent,Lake_type,Lake_area,Shore_len,Vol_total,Depth_avg,Dis_avg,Res_time,Grand_id,Pour_long,Pour_lat",
        "resultRecordCount": 5000,
        "f": "json",
    }
    headers = {"User-Agent": "WaterBodyResearchProject/1.0"}
    r = requests.get(url, params=params, headers=headers, timeout=120)
    r.raise_for_status()
    data = r.json()
    features = data.get("features", [])

    import csv
    if features:
        keys = list(features[0]["attributes"].keys())
        with open(dest, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys + ["geometry_x", "geometry_y"])
            writer.writeheader()
            for feat in features:
                row = feat["attributes"]
                geom = feat.get("geometry", {})
                row["geometry_x"] = geom.get("x")
                row["geometry_y"] = geom.get("y")
                writer.writerow(row)
        print(f"  ✓ Saved {len(features)} HydroLAKES records: {dest}")
    else:
        print("  ! No features returned from HydroLAKES REST service.")


def download_jrc_gsw_statistics():
    """
    Download JRC Global Surface Water monthly history statistics CSV.
    Available as direct CSV download from the JRC data portal.
    """
    # JRC provides per-country statistics as CSV
    dest = RAW_DIR / "jrc_gsw_statistics.csv"
    if dest.exists():
        print("  ✓ JRC GSW statistics already downloaded — skipping.")
        return

    # JRC GSW country statistics (all countries, permanent/seasonal/total)
    url = "https://global-surface-water.appspot.com/downloads/stats/jrc-gsw-country-statistics-v1_4.zip"
    zip_dest = RAW_DIR / "jrc_gsw_stats.zip"
    download_file(url, zip_dest, "JRC GSW country statistics")

    if zip_dest.exists():
        with zipfile.ZipFile(zip_dest, "r") as z:
            z.extractall(RAW_DIR)
        print(f"  ✓ JRC GSW statistics extracted to {RAW_DIR}")


if __name__ == "__main__":
    print("\n🌊 Water Body Data Download Pipeline")
    print("=" * 50)

    print("\n[1/3] Downloading HydroLAKES global lake database...")
    try:
        download_hydrolakes_sample()
    except Exception as e:
        print(f"  ! HydroLAKES download failed: {e}")

    print("\n[2/3] Downloading USGS Water Quality Portal data...")
    try:
        download_usgs_water_quality()
    except Exception as e:
        print(f"  ! USGS download failed: {e}")

    print("\n[3/3] Downloading JRC Global Surface Water statistics...")
    try:
        download_jrc_gsw_statistics()
    except Exception as e:
        print(f"  ! JRC GSW download failed: {e}")

    print("\n✅ Download complete. Run preprocess.py next.")

