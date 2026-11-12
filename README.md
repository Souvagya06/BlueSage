# 🌊 BlueSage — Historical Water Body Monitoring & Prediction Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3.1-61DAFB?style=flat-square&logo=react)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-5.4-646CFF?style=flat-square&logo=vite)](https://vitejs.dev/)
[![Leaflet](https://img.shields.io/badge/Leaflet-1.9.4-199900?style=flat-square&logo=leaflet)](https://leafletjs.com/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4.2-F7931E?style=flat-square&logo=scikit-learn)](https://scikit-learn.org/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python)](https://www.python.org/)

An end-to-end intelligent environmental monitoring platform that tracks 10 years of historical data (2014–2024) across global water bodies, implements spatial and temporal database indexing for real-time retrieval, and utilizes Machine Learning to classify water body types, assess water quality, and forecast environmental changes up to 10 years into the future.

---

## 👥 Project Team

| Name | Role / Focus |
|---|---|
| **Souvagya Karmakar** | Full-Stack Architecture, ML Pipeline & System Integration |
| **Sushmita Roy** | Data Engineering, Feature Processing & Classification Models |
| **Anirban Pal** | Spatial Indexing, Geospatial Mapping & Frontend Visualization |
| **Soumik Chattoraj** | Time-Series Forecasting Models & Environmental Metric Analysis |
| **Ronit Mishra** | Backend Services, API Optimization & Quality Assurance |

---

## 📌 Project Overview & Motivation

Water bodies—lakes, ponds, wetlands, rivers, and reservoirs—are vital life-support systems sustaining biodiversity, agriculture, and urban habitats. Rapid urbanization and climate change have accelerated degradation, shrinkage, and disappearance of critical freshwater bodies worldwide.

**BlueSage** tackles this challenge through a three-stage solution:
1. **Historical Data Assembly (2014–2024):** Curating a dedicated 10-year temporal dataset for 150+ water bodies combining satellite imagery indicators and in-situ physical/chemical measurements.
2. **Spatial & Temporal Indexing:** Structuring historical records with multi-dimensional database indexing (PostGIS GiST spatial indexes, B-Tree temporal indexes, and geohash spatial grid keys) for high-speed spatial proximity searches and queries.
3. **Triple-Task Machine Learning:**
   - **Task 1 — Water Body Type Classification:** Discriminating whether a body is a lake, pond, reservoir, wetland, or river.
   - **Task 2 — Water Quality Classification:** Grading water safety across five standard tiers (*Excellent, Good, Fair, Poor, Critical*).
   - **Task 3 — Future Change Prediction:** Forecasting decadal surface area trends (*Expand, Stable, Shrink, Disappear*) and projecting quantitative trajectories through 2034.

---

## 🌟 Key Features

- 🗺️ **Multi-Layer Interactive Map:** Search any global city (e.g., *Kolkata, Chicago, Geneva, Tokyo*) with instant viewport fly-to, colored quality status markers, and a layer switcher offering **Street (OSM)**, **Satellite (Esri)**, **Terrain (OpenTopoMap)**, **Dark (CartoDB)**, and **Light** views without external API keys.
- ⚡ **Zero-Postgres Instant Fallback:** Works completely out of the box! If PostgreSQL is not installed or running, the system automatically falls back to an in-memory spatial query engine powered by pre-indexed CSV datasets.
- 🔬 **Interactive ML Classification Studio:** Live on-demand prediction panel with dual-task tabs. Run trained Random Forest classifiers with real-time probability distribution bars.
- 📈 **Decadal Trend Visualizer:** Interactive Recharts charts rendering dual curves: solid lines for verified historical measurements (2014–2024) and dashed curves for ML forecast horizons (2025–2034).
- 💾 **One-Click Dataset Extraction:** Single-click export of the full indexed temporal dataset (`indexed_waterbody_dataset.csv` — 1,650 records, 21 standardized features).

---

## 📡 Real Data Sources

All historical observations in BlueSage are derived from verified global open scientific repositories:

| # | Data Source | Institution / Publisher | Parameters & Metrics Acquired | Access Method |
|---|---|---|---|---|
| **1** | **[HydroLAKES v1.0](https://www.hydrosheds.org/products/hydrolakes)** | McGill University & WWF | Global lake/reservoir registry, shoreline polygons, centroids, surface areas ($km^2$), depths | ArcGIS REST API |
| **2** | **[JRC Global Surface Water](https://global-surface-water.appspot.com/)** | European Commission JRC | 38 years of Landsat observations: Water occurrence %, seasonality (months/year), historical area dynamics | Open Research Archive (*Nature*) |
| **3** | **[USGS Water Quality Portal](https://www.waterqualitydata.us/)** | US Geological Survey & US EPA | Real sensor measurements: Dissolved Oxygen ($mg/L$), Turbidity ($NTU$), pH level, Chlorophyll-a ($\mu g/L$) | REST API (`/data/Result/search`) |
| **4** | **[OpenStreetMap Nominatim](https://nominatim.openstreetmap.org/)** | OpenStreetMap Foundation | City-to-coordinate geocoding & bounding box extraction | Open Geocoding API |

---

## 🧠 Machine Learning Architecture

```
                       ┌──────────────────────────────────────────────┐
                       │   Indexed Temporal Dataset (2014 - 2024)     │
                       │     150 Water Bodies · 1,650 Observations    │
                       └──────────────────────┬───────────────────────┘
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    ▼                         ▼                         ▼
         ┌─────────────────────┐   ┌─────────────────────┐   ┌─────────────────────┐
         │       TASK 1        │   │       TASK 2        │   │       TASK 3        │
         │  Type Classification│   │Quality Classification│  │ Future Change Pred. │
         ├─────────────────────┤   ├─────────────────────┤   ├─────────────────────┤
         │ Model: Random Forest│   │ Model: Random Forest│   │ Model: Polynomial + │
         │ Features: Area, NDWI│   │ Features: pH, DO,   │   │ Trend Classifier    │
         │ Occurrence, Months  │   │ Turbidity, Chl-a... │   │ Horizon: 10 Years   │
         │ Accuracy: ~90%      │   │ Accuracy: ~94%      │   │ Target: Area/Status │
         └─────────────────────┘   └─────────────────────┘   └─────────────────────┘
```

### 1. Task 1: Water Body Type Classifier
- **Objective:** Classify water body category into `Lake`, `Pond`, `Reservoir`, `Wetland`, or `River`.
- **Model:** Tuned `RandomForestClassifier` with balanced class weights.
- **Accuracy:** **~90%** test accuracy.
- **Artifacts:** `backend/ml/models/body_type_classifier.pkl`

### 2. Task 2: Water Quality Status Classifier
- **Objective:** Predict health category: `Excellent`, `Good`, `Fair`, `Poor`, or `Critical`.
- **Model:** `RandomForestClassifier` (200 estimators) trained on physical and biochemical indicators.
- **Accuracy:** **~94%** test accuracy (10-fold cross-validated F1 score: **0.907**).
- **Artifacts:** `backend/ml/models/classifier.pkl`

### 3. Task 3: Future Change Predictor
- **Objective:** Forecast whether a water body will `expand`, remain `stable`, `shrink`, or `disappear` based on decade-long area trajectory gradients.
- **Model:** Per-water-body polynomial trend regressor ($d=2$) projecting area, NDWI, and quality index through 2034.
- **Artifacts:** `backend/ml/models/predictor.pkl`

---

## 🗄️ Database Design & Indexing

When running with PostgreSQL 15 + PostGIS, BlueSage leverages hardware-accelerated spatial and text indexing:

| Index Name | Index Type | Target Column(s) | Operational Benefit |
|---|---|---|---|
| `idx_wb_centroid_gist` | **GiST (PostGIS)** | `water_bodies.centroid` | Fast k-Nearest Neighbors ($k$-NN) and radius searches |
| `idx_wb_country_type` | **B-Tree** | `country, water_body_type` | Instant filtering on composite categorical columns |
| `idx_obs_wb_year` | **B-Tree** | `water_body_id, observation_year` | Optimized sub-millisecond time-series joins |
| `idx_obs_year_ndwi` | **B-Tree** | `observation_year, ndwi` | Range scans on satellite index thresholds |
| `idx_wb_name_trgm` | **GIN (Trigram)** | `water_bodies.name` | Tolerant fuzzy text search for colloquial lake names |
| `spatial_grid_index` | **Discrete Geokey** | `GEO_LAT_LON` grid | In-memory O(1) hash lookups during offline fallback |

---

## 📁 Repository Structure

```
waterbody-project/
├── .gitignore                      # Git exclusion rules
├── README.md                       # Comprehensive project documentation
├── main.py                         # Root dual-runner script
├── run.bat                         # Quick-start batch runner
├── docker-compose.yml              # Container orchestration
│
├── backend/
│   ├── main.py                     # FastAPI entry point & unified SPA server
│   ├── run.bat                     # Windows launch script for backend
│   ├── database.py                 # SQLAlchemy engine & PostGIS connection
│   ├── config.py                   # Pydantic configuration settings
│   ├── requirements.txt            # Python dependencies
│   │
│   ├── models/waterbody.py         # SQLAlchemy ORM definitions
│   ├── schemas/waterbody.py        # Pydantic request/response schemas
│   ├── routers/                    # REST API routes
│   │   ├── waterbodies.py          # /api/waterbodies (CRUD, proximity, export)
│   │   ├── classification.py       # /api/classify (Tasks 1 & 2)
│   │   └── prediction.py           # /api/predict (Task 3)
│   ├── services/                   # Business logic & fallback providers
│   │   ├── mock_data.py            # High-speed in-memory indexed CSV provider
│   │   ├── retrieval.py            # Database query builder
│   │   ├── classifier.py           # ML inference services
│   │   └── predictor.py            # Decadal forecast services
│   ├── ml/                         # Model training scripts & saved binaries
│   │   ├── train_classifier.py
│   │   ├── train_body_type_classifier.py
│   │   ├── train_predictor.py
│   │   └── models/*.pkl
│   └── data_pipeline/              # ETL pipeline & database seeds
│       ├── export_indexed_dataset.py
│       ├── download_data.py
│       ├── preprocess.py
│       └── seed_db.py
│
├── data/
│   └── processed/                  # Indexed CSV datasets (10-year records)
│       ├── indexed_waterbody_dataset.csv
│       ├── water_bodies.csv
│       └── temporal_observations.csv
│
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── index.html                  # HTML entry point
    └── src/
        ├── App.jsx                 # Main layout, nav & routes
        ├── api/client.js           # Axios REST client
        ├── pages/
        │   ├── Dashboard.jsx       # Global statistics & data source registry
        │   ├── Explore.jsx         # Geospatial search, map & ML panel
        │   └── Predict.jsx         # 10-year trend forecast charts
        └── components/
            ├── WaterBodyMap.jsx    # Leaflet map with layer switcher
            ├── ClassificationPanel.jsx # Dual-task ML testing component
            ├── PredictionChart.jsx # Historical vs predicted time-series
            ├── FilterBar.jsx       # City search with Nominatim autocomplete
            └── WaterBodyTable.jsx  # Sortable, paginated data table
```

---

## 🚀 Quick Start Guide

### Option 1: Fast Start (No Database Required — Recommended)

The app includes an auto-bootstrap script that detects your virtual environment automatically:

```powershell
# Navigate to backend directory
cd backend

# Run directly (works with any Python — automatically delegates to venv)
python main.py
```

Open your browser at:
- **Web Dashboard:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive Swagger API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### Option 2: Full Stack with PostgreSQL + PostGIS (Optional)

If you wish to use the physical database with full spatial indexing:

1. **Install PostgreSQL 15 & PostGIS**, then open `psql`:
   ```sql
   CREATE DATABASE waterbody_db;
   CREATE USER waterbody_user WITH PASSWORD 'waterbody_pass_2024';
   GRANT ALL PRIVILEGES ON DATABASE waterbody_db TO waterbody_user;
   \c waterbody_db
   CREATE EXTENSION postgis;
   CREATE EXTENSION pg_trgm;
   ```

2. **Install Python dependencies & Seed Data:**
   ```powershell
   cd backend
   .\venv\Scripts\python.exe -m pip install -r requirements.txt
   .\venv\Scripts\python.exe data_pipeline/seed_db.py
   ```

3. **Start the platform:**
   ```powershell
   python main.py
   ```

---

### Option 3: Docker Deployment

```bash
docker-compose up --build
```
Access the application on `http://localhost:3000` (frontend) and `http://localhost:8000/docs` (backend).

---

## 🛠️ API Reference Summary

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/waterbodies/` | Query water bodies with categorical, quality & temporal filters |
| `GET` | `/api/waterbodies/near` | Spatial proximity search (`lat`, `lon`, `radius_km`) |
| `GET` | `/api/waterbodies/bbox` | Bounding box spatial retrieval (`min_lat`, `max_lat`, ...) |
| `GET` | `/api/waterbodies/{id}` | Detailed water body profile with 10-year observations |
| `GET` | `/api/waterbodies/export-csv` | Direct download of the entire indexed CSV dataset |
| `POST`| `/api/classify/body-type` | **Task 1:** ML water body type classification |
| `POST`| `/api/classify/` | **Task 2:** ML water quality grade classification |
| `GET` | `/api/predict/{id}` | **Task 3:** 10-year projection of area, NDWI & trend |

---

## 📜 License

This project was developed for academic and environmental monitoring research purposes. Datasets sourced from HydroLAKES, USGS WQP, JRC GSW, and OpenStreetMap belong to their respective institutions under their respective open-access licenses.
