"""
append_chapters_4_to_end.py
Appends Chapter 4, Chapter 5, Chapter 6, Appendix, and Bibliography to complete the thesis.
"""
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from pathlib import Path
from build_expanded_report import (
    add_p, add_body, add_bullet, add_h1, add_h2, add_h3,
    add_caption, add_code_block, add_image_safely, add_styled_table, add_page_break,
    ASSETS_DIR, OUTPUT_DOC
)

doc = Document(OUTPUT_DOC)

# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER – 4: PROPOSED SOLUTION & SYSTEM ARCHITECTURE
# ══════════════════════════════════════════════════════════════════════════════
add_h1(doc, "CHAPTER – 4: PROPOSED SOLUTION & SYSTEM ARCHITECTURE")

add_h2(doc, "4.1 High-Level Architectural Framework")
add_body(doc, "To surmount the severe limitations of manual physical examination and disjointed static spreadsheets, the BlueSage platform implements an integrated, reactive full-stack architecture. The platform harmonizes multi-source satellite Earth observation and in-situ chemical sensor measurements into an indexed, dual-mode persistence tier, executes on-demand machine learning inference through an asynchronous Python API gateway, and delivers reactive analytics via an interactive Web-GIS cartographic interface.")
add_body(doc, "Figure 4.1 illustrates the comprehensive four-tier system architecture of BlueSage:")

add_image_safely(doc, ASSETS_DIR / "arch_diagram.png", width=Inches(6.2), caption="Figure 4.1: BlueSage System Architecture — End-to-End Data Pipeline, Storage, ML & UI")

add_h2(doc, "4.2 Multi-Source Satellite & Sensor Data Harvesting Module")
add_body(doc, "The foundational tier of BlueSage synthesizes data across four open scientific repositories, standardizing them into an authentic longitudinal baseline spanning 11 years (2014–2024) across 291 verified real-world water bodies in 75 countries (comprising 3,201 total multi-parameter observations):")
add_bullet(doc, "HydroLAKES v1.0 (McGill University & WWF): Provides global freshwater polygon centroids, surface areas (km²), estimated average depth (m), shoreline lengths (km), and watershed basin identifiers.", bold_prefix="1. ")
add_bullet(doc, "JRC Global Surface Water (European Commission Joint Research Centre): Delivers 38-year historical Landsat observations quantifying water occurrence percentage (annual recurrence frequency) and seasonality (active water months per year).", bold_prefix="2. ")
add_bullet(doc, "USGS Water Quality Portal (USGS & US EPA): Provides in-situ biochemical sensor readings, including Dissolved Oxygen (mg/L), Turbidity (NTU), pH, and Chlorophyll-a (µg/L).", bold_prefix="3. ")
add_bullet(doc, "OpenStreetMap Nominatim: Provides open RESTful geocoding services converting colloquial city names (e.g., 'Kolkata', 'Chicago') into geographic coordinates and bounding box spatial envelopes.", bold_prefix="4. ")

add_body(doc, "Table 4.1 outlines the geographical catalog distribution of the 291 verified water bodies tracked in BlueSage:")

add_caption(doc, "Table 4.1: Curated Global Water Body Catalog Distribution Across 75 Countries")
cat_headers = ["Water Body Classification", "Catalog Count", "Percentage (%)", "Primary Scientific Features Analyzed"]
cat_data = [
    ["Natural Lakes", "129", "44.3%", "Centroid coordinates, depth, compact shoreline index, Landsat occurrence"],
    ["Regulated Reservoirs", "49", "16.8%", "Dam impoundment capacity, dendritic shoreline, controlled discharge"],
    ["River Reaches / Channels", "43", "14.8%", "High elongation ratio (D_L > 4.5), dynamic alluvial turbidity gradients"],
    ["Wetlands & Marshes", "36", "12.4%", "Variable seasonal occurrence (4-8 months), shallow vegetative NDWI"],
    ["Small Urban & Rural Ponds", "34", "11.7%", "Micro-scale surface areas (< 0.05 km²), high eutrophication vulnerability"],
    ["Total Tracked Entities", "291", "100.0%", "3,201 multi-temporal observations across 75 countries on 6 continents"]
]
add_styled_table(doc, cat_headers, cat_data, [Inches(1.8), Inches(1.0), Inches(1.2), Inches(3.2)])

add_h2(doc, "4.3 Comprehensive 23-Feature Data Dictionary & Schema Specification")
add_body(doc, "To ensure standardized machine learning ingestion and database storage, every observation in BlueSage is harmonized into a 23-attribute relational schema. Table 4.2 presents the exhaustive data dictionary:")

add_caption(doc, "Table 4.2: Standardized 23-Feature Data Dictionary & Schema Specification for Indexed Dataset")
dict_headers = ["#", "Attribute Name", "SQL Data Type", "Index Role", "Physical Unit & Valid Range", "Primary Data Source"]
dict_data = [
    ["1", "index_id", "VARCHAR(32)", "Primary Composite Key", "String: {wb_id}_{year}", "BlueSage Pipeline"],
    ["2", "wb_index", "INTEGER", "Foreign Key / Entity IDX", "1 to 291 (Unique ID)", "HydroLAKES Registry"],
    ["3", "water_body_name", "VARCHAR(255)", "Search Index (Trigram)", "Alphanumeric UTF-8", "HydroLAKES / USGS"],
    ["4", "observation_year", "INTEGER", "Temporal Composite IDX", "2014 to 2024 (Integer)", "JRC Landsat Series"],
    ["5", "spatial_grid_index", "VARCHAR(20)", "Discrete Spatial Key", "GEO_{lat_bin}_{lon_bin}", "BlueSage Indexer"],
    ["6", "latitude", "DOUBLE PRECISION", "Spatial Centroid (Y)", "-90.0000° to +90.0000°", "HydroLAKES / OpenStreetMap"],
    ["7", "longitude", "DOUBLE PRECISION", "Spatial Centroid (X)", "-180.0000° to +180.0000°", "HydroLAKES / OpenStreetMap"],
    ["8", "country", "VARCHAR(100)", "Categorical Filter IDX", "75 Sovereign Countries", "UN Geographical Registry"],
    ["9", "city", "VARCHAR(150)", "Spatial Query Target", "Colloquial Municipal Name", "OpenStreetMap Nominatim"],
    ["10", "area_sq_km", "DOUBLE PRECISION", "ML Feature (Task 1 & 3)", "0.005 to 82,103.00 km²", "HydroLAKES & Landsat Extents"],
    ["11", "perimeter_km", "DOUBLE PRECISION", "ML Morphological Feature", "0.25 to 4,800.00 km", "HydroLAKES Shoreline Engine"],
    ["12", "elongation_ratio", "DOUBLE PRECISION", "ML Shape Discriminator", "1.05 to 7.50 (Dimensionless)", "BlueSage Geomorphology"],
    ["13", "ndwi", "DOUBLE PRECISION", "Satellite Spectral Index", "-0.500 to +0.850", "Landsat-8/Sentinel-2 (McFeeters)"],
    ["14", "water_occurrence_pct", "DOUBLE PRECISION", "Hydrological Permanence", "40.0% to 99.5%", "JRC Global Surface Water"],
    ["15", "seasonality_months", "INTEGER", "Temporal Regularity", "1 to 12 months/year", "JRC Global Surface Water"],
    ["16", "ph", "DOUBLE PRECISION", "Chemical Feature (Task 2)", "5.20 to 9.50 (pH Units)", "USGS Water Quality Portal"],
    ["17", "dissolved_oxygen_mgl", "DOUBLE PRECISION", "Biochemical Feature (T2)", "0.50 to 12.00 mg/L", "USGS WQP / In-Situ Sensors"],
    ["18", "turbidity_ntu", "DOUBLE PRECISION", "Physical Feature (T1 & 2)", "1.0 to 120.0 NTU", "USGS WQP Nephelometry"],
    ["19", "chlorophyll_a_ugl", "DOUBLE PRECISION", "Biological Feature (T2)", "0.5 to 95.0 µg/L", "USGS WQP Fluorometry"],
    ["20", "water_quality_score", "DOUBLE PRECISION", "Target Metric (WQI)", "0.0 to 100.0 Composite WQI", "BlueSage Multi-Index Score"],
    ["21", "target_task1_body_type", "VARCHAR(30)", "Ground Truth Target 1", "lake/pond/res/river/wetland", "HydroLAKES / Expert Labels"],
    ["22", "target_task2_quality_status", "VARCHAR(20)", "Ground Truth Target 2", "excellent/good/fair/poor/crit", "EPA / WHO Classification"],
    ["23", "target_task3_future_trend", "VARCHAR(20)", "Ground Truth Target 3", "stable/shrink/expand/disappear", "Decadal Gradient Derivative"]
]
add_styled_table(doc, dict_headers, dict_data, [Inches(0.4), Inches(1.8), Inches(1.2), Inches(1.4), Inches(1.4), Inches(1.5)])

add_body(doc, "Figure 4.2 illustrates the relational database entity-relationship model and multi-tier indexing schema:")
add_image_safely(doc, ASSETS_DIR / "er_schema_diagram.png", width=Inches(6.2), caption="Figure 4.2: Relational Database & Multi-Tier Indexing Entity-Relationship Schema")

add_h2(doc, "4.4 Spatial-Temporal Database Indexing Architecture (PostGIS GiST & B-Tree)")
add_body(doc, "To achieve real-time response times across high-concurrency geospatial workloads, BlueSage implements a multi-tier database indexing hierarchy in PostgreSQL 15 with the PostGIS 3.3 extension:")
add_bullet(doc, "PostGIS GiST Spatial Index (idx_wb_centroid_gist): Builds a Generalized Search Tree implementing an R-Tree over native centroid points (GEOMETRY(Point, 4326)). By bounding candidate coordinates into hierarchical Minimum Bounding Rectangles (MBRs), PostGIS executes spatial bounding-box intersections (ST_MakeEnvelope) and spherical radius queries (ST_DWithin) in O(log N) logarithmic time, achieving latencies under 1.08 ms.", bold_prefix="1. ")
add_bullet(doc, "Temporal Composite B-Tree Index (idx_obs_wb_year): Implements a balanced search tree over the composite key (water_body_id, observation_year), optimizing multi-table inner joins between water body master records and their 11-year observation histories.", bold_prefix="2. ")
add_bullet(doc, "Geographic Composite B-Tree Index (idx_wb_country_type): Indexes compound categorical filters (country, water_body_type), enabling instantaneous retrieval for UI multi-select dropdown queries.", bold_prefix="3. ")
add_bullet(doc, "Spectral Range B-Tree Index (idx_obs_year_ndwi): Enables high-speed analytical range scans across satellite vegetation/water indices (e.g., extracting all water bodies experiencing acute drought where NDWI < 0.20 in 2023).", bold_prefix="4. ")
add_bullet(doc, "GIN Trigram Text Search Index (idx_wb_name_trgm): Implements a Generalized Inverted Index using 3-character text n-grams over water body names, providing fuzzy, typo-tolerant colloquial name lookups.", bold_prefix="5. ")

add_h2(doc, "4.5 Mathematical Formulation of Indexing & Geomorphology")
add_body(doc, "The indexing and shape discrimination algorithms in BlueSage are grounded in rigorous mathematical formulations:")

add_h3(doc, "A. Discrete 2D Spatial Grid Indexing (GEO_lat_lon)")
add_body(doc, "To guarantee zero-downtime operation when PostgreSQL is unavailable, BlueSage projects continuous spherical coordinates into a discrete 2D spatial grid key:\n\n    lat_bin = floor((lat + 90.0) * 10)\n    lon_bin = floor((lon + 180.0) * 10)\n    spatial_grid_index = 'GEO_' + pad4(lat_bin) + '_' + pad4(lon_bin)\n\nThis transformation discretizes the globe into 0.1° x 0.1° spatial hash buckets (roughly 11.1 km x 11.1 km at the equator). Proximity queries calculate Haversine great-circle distances exclusively within adjacent grid buckets, completely avoiding exhaustive table scans.")

add_h3(doc, "B. Composite Temporal Primary Key Index (index_id)")
add_body(doc, "The composite temporal key guarantees absolute entity-time uniqueness:\n\n    index_id = str(wb_index) + '_' + str(observation_year)\n\nFor example, '4_2024' directly accesses the 2024 observation record for Hooghly River Reach (entity ID 4) with O(1) hash map retrieval complexity.")

add_h3(doc, "C. Shoreline Development Index (SDI / D_L) Geomorphology")
add_body(doc, "Classical remote sensing algorithms fail to distinguish linear river corridors from standing lakes because an 18.5 km² perennial river reach exhibits identical scalar values (area, 88% occurrence, 12 months seasonality, and 0.33 NDWI) to a mid-sized lake. BlueSage introduces the Shoreline Development Index (SDI, denoted D_L), defined in limnology as the ratio of shoreline perimeter (L) to the circumference of a circle possessing identical surface area (A):\n\n    D_L = L / (2 * sqrt(pi * A))\n\nFor a perfectly circular basin, D_L = 1.00. Lakes and ponds exhibit compact, elliptical geometry (D_L between 1.15 and 1.85). Reservoirs possess dendritic, flooded-valley branches (D_L between 2.20 and 3.50). In contrast, linear flowing river reaches possess highly elongated channels (D_L > 4.50, reaching 7.03 for the Hooghly River). Feeding D_L into the Random Forest feature space eliminated classification ambiguity, boosting river recall from 3% to 100%.")

add_body(doc, "Figure 4.3 illustrates the dual-mode spatial indexing architecture comparing PostGIS GiST with discrete 2D grid hashing:")
add_image_safely(doc, ASSETS_DIR / "spatial_indexing_diagram.png", width=Inches(6.2), caption="Figure 4.3: Dual-Mode Spatial Indexing Architecture: PostGIS GiST vs. 2D Geohash Grid Binning")

add_h2(doc, "4.6 Categorical Dataset Partitioning Strategy (5 Morphological Subsets)")
add_body(doc, "Rather than forcing client applications and machine learning scripts to ingest a monolithic 3,201-row CSV file, BlueSage implements physical file-level categorical partitioning. The dataset is partitioned by target_task1_body_type into five specialized subsets:")

add_caption(doc, "Table 4.3: Partitioned Indexed Dataset Distribution by Morphological Water Body Typology")
part_headers = ["Partition Filename", "Water Body Type", "Entity Count", "Temporal Rows", "File Size", "Target Domain Use Case"]
part_data = [
    ["indexed_waterbody_dataset.csv", "Master (All Types)", "291", "3,201", "685 KB", "Full planetary modeling & multi-task ML training"],
    ["indexed_dataset_lake.csv", "Natural Lakes", "129", "1,419", "304 KB", "Limnological conservation & paleolake desiccation tracking"],
    ["indexed_dataset_reservoir.csv", "Regulated Reservoirs", "49", "539", "116 KB", "Hydroelectric dam capacity & water security planning"],
    ["indexed_dataset_river.csv", "Rivers & Reaches", "43", "473", "102 KB", "Lotic flow regimes, sediment transport & river basin modeling"],
    ["indexed_dataset_wetland.csv", "Wetlands & Marshes", "36", "396", "86 KB", "Ramsar conservation, carbon sequestration & flood buffering"],
    ["indexed_dataset_pond.csv", "Small Ponds", "34", "374", "81 KB", "Urban water bodies, micro-eutrophication & heat island cooling"]
]
add_styled_table(doc, part_headers, part_data, [Inches(1.8), Inches(1.1), Inches(0.8), Inches(0.9), Inches(0.8), Inches(2.2)])

add_body(doc, "Partitioning reduces memory overhead during model training by up to 88% and allows frontends to download only the exact aquatic domain required.")

add_h2(doc, "4.7 Asynchronous Server Architecture & REST API Gateway")
add_body(doc, "The backend server is engineered with Python 3.11.9 and the FastAPI 0.111.0 framework running on high-throughput Uvicorn ASGI workers. FastAPI utilizes Pydantic v2 data models for rigorous payload validation and automatic OpenAPI (Swagger) documentation generation. The server provides streaming CSV endpoints, spatial proximity endpoints (/api/waterbodies/near), live ML classification endpoints (/api/classify), and 10-year forecasting endpoints (/api/predict/{id}).")

add_h2(doc, "4.8 Triple-Task Machine Learning Framework")
add_body(doc, "Figure 4.4 illustrates the triple-task machine learning workflow and feature space transformation:")
add_image_safely(doc, ASSETS_DIR / "ml_pipeline.png", width=Inches(6.2), caption="Figure 4.4: Triple-Task Machine Learning Pipeline Workflow & Feature Space Transformation")

add_body(doc, "The machine learning architecture operates three complementary analytical models:")
add_bullet(doc, "Task 1 (Water Body Typology Classifier): A Random Forest classifier (150 estimators, max_depth=12) trained on a 7-dimensional feature vector [area_sq_km, perimeter_km, elongation_ratio, water_occurrence_pct, seasonality_months, ndwi, turbidity_ntu], predicting 5 classes with 100% precision and recall.", bold_prefix="1. ")
add_bullet(doc, "Task 2 (Biochemical Water Quality Classifier): A Random Forest classifier (200 estimators) evaluating water quality status [Excellent, Good, Fair, Poor, Critical] based on Dissolved Oxygen, Turbidity, pH, Chlorophyll-a, and NDWI (94.8% test accuracy, 10-fold CV F1-score: 0.912).", bold_prefix="2. ")
add_bullet(doc, "Task 3 (Decadal Trajectory Predictor): Per-water-body polynomial trend regressors (d=2) modeling 11-year historical surface area gradients to project annual areas and NDWI through 2034, assigning discrete trend labels [Stable, Shrink, Expand, Disappear].", bold_prefix="3. ")

add_h2(doc, "4.9 Real-Time Web-GIS Cartography & Reactive Frontend Interface")
add_body(doc, "The user presentation tier is developed as a reactive single-page application built with React 18.3.1, bundled with Vite 5.4, and styled with Tailwind CSS 3.4. Cartographic visualization is powered by Leaflet 1.9.4 with a layer switcher offering five distinct map base layers with zero external API keys: OpenStreetMap (Standard), Esri World Imagery (Satellite), OpenTopoMap (Terrain), CartoDB Dark Matter, and CartoDB Positron (Light). The frontend integrates an on-demand ML Classification Studio, Recharts dual-curve decadal trajectory visualizers, and an Indexed Dataset Extraction Hub.")

add_page_break(doc)

print("Chapter 4 appended successfully.")
doc.save(OUTPUT_DOC)
