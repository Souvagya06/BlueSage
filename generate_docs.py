"""
generate_docs.py
Generates high-resolution architecture diagrams and compiles a comprehensive,
onboarding-ready Microsoft Word document (.docx) for the BlueSage project.
"""
import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

OUT_DIR = Path("E:/Hackathons/Inno_4th_year/waterbody-project")
DOC_PATH = OUT_DIR / "BlueSage_Project_Documentation.docx"
IMG_DIR = OUT_DIR / "docs_assets"
IMG_DIR.mkdir(parents=True, exist_ok=True)

# ─── 1. Generate Diagram 1: Full System Architecture ──────────────────────────
def create_architecture_diagram():
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Title
    ax.text(50, 96, "BlueSage System Architecture", ha="center", va="center", fontsize=15, fontweight="bold", color="#1e3a8a")
    ax.text(50, 92, "End-to-End Data Pipeline, Dual-Mode Storage, ML Engine & Presentation Layer", ha="center", va="center", fontsize=9.5, color="#64748b")

    # Colors
    c_data = "#eff6ff"     # blue
    c_data_b = "#3b82f6"
    c_db = "#f0fdf4"       # green
    c_db_b = "#22c55e"
    c_ml = "#fefce8"       # yellow
    c_ml_b = "#eab308"
    c_ui = "#faf5ff"       # purple
    c_ui_b = "#a855f7"

    # Layer 1: Data Sources
    ax.add_patch(patches.FancyBboxPatch((4, 73), 92, 15, boxstyle="round,pad=1.5", ec=c_data_b, fc=c_data, lw=1.5))
    ax.text(7, 85, "LAYER 1: DATA SOURCES & HARVESTING", fontsize=10, fontweight="bold", color="#1d4ed8")
    
    sources = [
        ("HydroLAKES v1.0", "Registry, centroid, area, depth, shoreline"),
        ("JRC Global Surface Water", "38-yr Landsat, occurrence %, seasonality"),
        ("USGS Water Quality Portal", "In-situ pH, DO (mg/L), Turbidity, Chl-a"),
        ("OSM Nominatim", "City geocoding & bounding box API")
    ]
    for i, (title, sub) in enumerate(sources):
        x = 7 + i * 22.5
        ax.add_patch(patches.FancyBboxPatch((x, 75), 21, 8.5, boxstyle="round,pad=0.8", ec="#93c5fd", fc="white", lw=1))
        ax.text(x + 10.5, 80.5, title, ha="center", va="center", fontsize=8.5, fontweight="bold", color="#1e40af")
        ax.text(x + 10.5, 77.2, sub, ha="center", va="center", fontsize=6.8, color="#475569", wrap=True)

    # Layer 2: Storage & Indexing
    ax.add_patch(patches.FancyBboxPatch((4, 49), 92, 17, boxstyle="round,pad=1.5", ec=c_db_b, fc=c_db, lw=1.5))
    ax.text(7, 63, "LAYER 2: INDEXED RETRIEVAL & DUAL EXECUTION ENGINE", fontsize=10, fontweight="bold", color="#15803d")

    # DB block 1
    ax.add_patch(patches.FancyBboxPatch((7, 51.5), 42, 9.5, boxstyle="round,pad=0.8", ec="#86efac", fc="white", lw=1))
    ax.text(28, 58, "Mode A: PostgreSQL 15 + PostGIS 3.3", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#166534")
    ax.text(28, 54, "• GiST Spatial Index (idx_wb_centroid_gist)\n• B-Tree Temporal & NDWI (idx_obs_wb_year)\n• GIN Trigram Fuzzy Search (idx_wb_name_trgm)", ha="center", va="center", fontsize=7.2, color="#374151")

    # DB block 2
    ax.add_patch(patches.FancyBboxPatch((51, 51.5), 42, 9.5, boxstyle="round,pad=0.8", ec="#86efac", fc="white", lw=1))
    ax.text(72, 58, "Mode B: Zero-Postgres Instant Fallback", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#166534")
    ax.text(72, 54, "• Pre-indexed 10-Yr Dataset (indexed_waterbody_dataset.csv)\n• Spatial Grid Geokey Index (GEO_LAT_LON)\n• In-Memory Haversine k-NN Query Engine", ha="center", va="center", fontsize=7.2, color="#374151")

    # Layer 3: Backend & ML Engine
    ax.add_patch(patches.FancyBboxPatch((4, 25), 92, 17, boxstyle="round,pad=1.5", ec=c_ml_b, fc=c_ml, lw=1.5))
    ax.text(7, 39, "LAYER 3: FASTAPI REST BACKEND & TRIPLE-TASK ML PIPELINE", fontsize=10, fontweight="bold", color="#a16207")

    ml_tasks = [
        ("Task 1: Type Classifier", "Random Forest (~90% Acc)\nLake / Pond / River / Wetland / Res"),
        ("Task 2: Quality Classifier", "Random Forest (200 trees, ~94% Acc)\nExcellent / Good / Fair / Poor / Critical"),
        ("Task 3: Future Predictor", "Polynomial Reg. + Trend Analysis\n10-Yr Area, NDWI & Trajectory Forecast"),
        ("FastAPI Core & Router", "Proximity search, GeoJSON, CSV Export,\nUnified SPA Static Files Server")
    ]
    for i, (title, sub) in enumerate(ml_tasks):
        x = 7 + i * 22.5
        ax.add_patch(patches.FancyBboxPatch((x, 27), 21, 10, boxstyle="round,pad=0.8", ec="#fde047", fc="white", lw=1))
        ax.text(x + 10.5, 33.5, title, ha="center", va="center", fontsize=8, fontweight="bold", color="#854d0e")
        ax.text(x + 10.5, 29.8, sub, ha="center", va="center", fontsize=6.8, color="#475569")

    # Layer 4: Frontend UI
    ax.add_patch(patches.FancyBboxPatch((4, 3), 92, 15, boxstyle="round,pad=1.5", ec=c_ui_b, fc=c_ui, lw=1.5))
    ax.text(7, 15, "LAYER 4: REACT 18 + VITE INTERACTIVE PRESENTATION", fontsize=10, fontweight="bold", color="#7e22ce")

    ui_blocks = [
        ("Dashboard Page", "Global KPI stats, quality counters, data source registry, dataset download"),
        ("Explore Map Studio", "City search, 5-layer Leaflet map, instant sync, detailed physical cards"),
        ("Predictive Studio", "Recharts historical vs forecast curves, decadal trend risk indicators"),
        ("ML Control Panel", "Live classification inference with animated probability distribution bars")
    ]
    for i, (title, sub) in enumerate(ui_blocks):
        x = 7 + i * 22.5
        ax.add_patch(patches.FancyBboxPatch((x, 5), 21, 8.5, boxstyle="round,pad=0.8", ec="#d8b4fe", fc="white", lw=1))
        ax.text(x + 10.5, 10.5, title, ha="center", va="center", fontsize=8, fontweight="bold", color="#6b21a8")
        ax.text(x + 10.5, 7.2, sub, ha="center", va="center", fontsize=6.5, color="#475569")

    # Connecting arrows
    for y in [73, 49, 25]:
        ax.annotate("", xy=(50, y), xytext=(50, y + 2),
                    arrowprops=dict(arrowstyle="->", lw=2, color="#475569"))

    plt.tight_layout()
    p = IMG_DIR / "arch_diagram.png"
    plt.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close()
    return p

# ─── 2. Generate Diagram 2: Machine Learning Workflow ─────────────────────────
def create_ml_diagram():
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    ax.text(50, 95, "BlueSage Triple-Task ML Pipeline Workflow", ha="center", va="center", fontsize=14, fontweight="bold", color="#0f766e")
    ax.text(50, 90, "From 10-Year Temporal Observation Vectors to Actionable Environmental Predictions", ha="center", va="center", fontsize=9, color="#64748b")

    # Input Node
    ax.add_patch(patches.FancyBboxPatch((3, 48), 24, 30, boxstyle="round,pad=1.2", ec="#0d9488", fc="#ccfbf1", lw=1.5))
    ax.text(15, 74, "10-Year Temporal Data", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#115e59")
    features_text = "• Surface Area (km²)\n• NDWI (Min, Max, Avg)\n• Water Occurrence %\n• Seasonality (mo/yr)\n• pH & Turbidity (NTU)\n• Dissolved O₂ (mg/L)\n• Chlorophyll-a (µg/L)\n• Spatial Grid Index"
    ax.text(15, 60, features_text, ha="center", va="center", fontsize=7.5, color="#134e4a")

    # Arrow from Input to Tasks
    ax.annotate("", xy=(34, 75), xytext=(28, 65), arrowprops=dict(arrowstyle="->", lw=1.8, color="#0d9488"))
    ax.annotate("", xy=(34, 55), xytext=(28, 63), arrowprops=dict(arrowstyle="->", lw=1.8, color="#0d9488"))
    ax.annotate("", xy=(34, 35), xytext=(28, 61), arrowprops=dict(arrowstyle="->", lw=1.8, color="#0d9488"))

    # Task 1 Box
    ax.add_patch(patches.FancyBboxPatch((35, 68), 34, 18, boxstyle="round,pad=1", ec="#2563eb", fc="#eff6ff", lw=1.5))
    ax.text(52, 82, "TASK 1: Water Body Type Classifier", ha="center", va="center", fontsize=9, fontweight="bold", color="#1d4ed8")
    ax.text(52, 75, "RandomForestClassifier · 150 estimators\nInputs: Area, NDWI, Occurrence, Seasonality", ha="center", va="center", fontsize=7.5, color="#1e40af")
    ax.text(52, 70.5, "Metric: ~90% Test Accuracy (Balanced)", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#16a34a")

    # Task 2 Box
    ax.add_patch(patches.FancyBboxPatch((35, 46), 34, 18, boxstyle="round,pad=1", ec="#16a34a", fc="#f0fdf4", lw=1.5))
    ax.text(52, 60, "TASK 2: Water Quality Status Classifier", ha="center", va="center", fontsize=9, fontweight="bold", color="#15803d")
    ax.text(52, 53, "RandomForestClassifier · 200 estimators\nInputs: pH, DO, Turbidity, Chl-a, NDWI", ha="center", va="center", fontsize=7.5, color="#166534")
    ax.text(52, 48.5, "Metric: ~94% Test Accuracy · 10-Fold CV: 0.907", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#16a34a")

    # Task 3 Box
    ax.add_patch(patches.FancyBboxPatch((35, 24), 34, 18, boxstyle="round,pad=1", ec="#9333ea", fc="#faf5ff", lw=1.5))
    ax.text(52, 38, "TASK 3: Future Change Trend Predictor", ha="center", va="center", fontsize=9, fontweight="bold", color="#7e22ce")
    ax.text(52, 31, "Polynomial Reg. (degree=2) + Slope Trajectory\nHorizon: 10 Years Ahead (2025–2034)", ha="center", va="center", fontsize=7.5, color="#6b21a8")
    ax.text(52, 26.5, "Target: Decadal Area, NDWI & Status Trends", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#9333ea")

    # Arrows to Outputs
    for y in [77, 55, 33]:
        ax.annotate("", xy=(74, y), xytext=(70, y), arrowprops=dict(arrowstyle="->", lw=1.8, color="#475569"))

    # Outputs
    outputs = [
        (75, 68, "#eff6ff", "#2563eb", "Predicted Water Body Type", "• Lake\n• Pond\n• Reservoir\n• Wetland\n• River"),
        (75, 46, "#f0fdf4", "#16a34a", "Predicted Quality Status", "• Excellent\n• Good\n• Fair\n• Poor\n• Critical"),
        (75, 24, "#faf5ff", "#9333ea", "10-Year Decadal Forecast", "• Trend: Expand/Stable/Shrink/Disappear\n• Quantitative Surface Area Trajectory\n• Health Projection Through 2034")
    ]
    for x, y, bg, border, title, desc in outputs:
        ax.add_patch(patches.FancyBboxPatch((x, y), 22, 18, boxstyle="round,pad=0.8", ec=border, fc=bg, lw=1.2))
        ax.text(x + 11, y + 15, title, ha="center", va="center", fontsize=8, fontweight="bold", color=border)
        ax.text(x + 11, y + 8, desc, ha="center", va="center", fontsize=7, color="#374151")

    plt.tight_layout()
    p = IMG_DIR / "ml_pipeline.png"
    plt.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close()
    return p

# ─── Helper for Word Styling ──────────────────────────────────────────────────
def style_table(table, header_bg="1E3A8A", row_alt_bg="F8FAFC"):
    for i, row in enumerate(table.rows):
        for cell in row.cells:
            # cell padding
            tcPr = cell._tc.get_or_add_tcPr()
            tcMar = OxmlElement('w:tcMar')
            for m in ['top', 'bottom']:
                node = OxmlElement(f'w:{m}')
                node.set(qn('w:w'), '120')
                node.set(qn('w:type'), 'dxa')
                tcMar.append(node)
            for m in ['left', 'right']:
                node = OxmlElement(f'w:{m}')
                node.set(qn('w:w'), '160')
                node.set(qn('w:type'), 'dxa')
                tcMar.append(node)
            tcPr.append(tcMar)

            if i == 0:
                shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{header_bg}"/>')
                tcPr.append(shading)
                for p in cell.paragraphs:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    for run in p.runs:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(255, 255, 255)
                        run.font.size = Pt(9.5)
            else:
                if i % 2 == 1:
                    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{row_alt_bg}"/>')
                    tcPr.append(shading)
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.size = Pt(9)
                        run.font.color.rgb = RGBColor(30, 41, 59)

# ─── Main Document Builder ────────────────────────────────────────────────────
def build_document():
    doc = Document()

    # Page Margins
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # ── Cover / Header ──
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(12)
    title_p.paragraph_format.space_after = Pt(2)
    title_run = title_p.add_run("🌊 BlueSage — Global Water Body Monitoring & Prediction Platform")
    title_run.font.size = Pt(22)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(30, 58, 138)  # Navy blue

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(16)
    sub_run = sub_p.add_run("Comprehensive Technical Documentation, System Architecture & Developer Onboarding Manual")
    sub_run.font.size = Pt(12)
    sub_run.font.italic = True
    sub_run.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # ── Section 1: Team Members ──
    h1 = doc.add_heading("1. Project Identity & Team Roster", level=1)
    h1.paragraph_format.space_before = Pt(12)
    h1.paragraph_format.space_after = Pt(6)

    doc.add_paragraph(
        "BlueSage was developed as an end-to-end environmental intelligence platform for the 4th-Year Computer Science "
        "& Engineering / AI Capstone. The project integrates multi-spectral satellite remote sensing, temporal database indexing, "
        "and machine learning to model water body dynamics across 10 years (2014–2024) and forecast changes through 2034."
    )

    table = doc.add_table(rows=6, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Member Name", "Core Role", "Domain Responsibilities"]
    for j, h in enumerate(headers):
        table.cell(0, j).paragraphs[0].text = h

    members = [
        ("Souvagya Karmakar", "Full-Stack Architecture & Lead Integration", "System design, FastAPI routers, unified execution engine, ML integration & deployment."),
        ("Sushmita Roy", "Data Engineering & Classification ML", "Multi-source ETL pipelines, feature engineering, Task 1 & Task 2 Random Forest classifiers."),
        ("Anirban Pal", "Spatial Indexing & GIS Visualizations", "PostGIS GiST indexing, geohash spatial keys, multi-layer Leaflet interactive mapping studio."),
        ("Soumik Chattoraj", "Time-Series Forecasting & Analysis", "Task 3 decadal prediction models, polynomial trajectory regressors, NDWI trend analysis."),
        ("Ronit Mishra", "Backend Services & API Optimization", "API endpoint scaling, CORS handling, query optimization, QA testing & data validation.")
    ]
    for i, (name, role, resp) in enumerate(members, start=1):
        table.cell(i, 0).paragraphs[0].text = name
        table.cell(i, 1).paragraphs[0].text = role
        table.cell(i, 2).paragraphs[0].text = resp
    style_table(table)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # ── Section 2: Executive Summary & Motivation ──
    h2 = doc.add_heading("2. Executive Summary & Problem Motivation", level=1)
    doc.add_paragraph(
        "Freshwater bodies (lakes, reservoirs, wetlands, rivers, and ponds) represent Earth's most critical yet endangered ecosystems. "
        "Urban expansion, agricultural drainage, and climate variability have caused widespread shrinkage and pollution of water bodies. "
        "Traditional water assessment methods rely either on expensive, infrequent manual sampling or complex, inaccessible satellite GIS toolsets."
    )
    doc.add_paragraph(
        "BlueSage bridges this gap by creating a unified, high-speed monitoring platform that achieves three fundamental goals:\n"
        "1. Dedicated 10-Year Temporal Dataset: Synthesizes physical, chemical, and satellite indicators from 2014 through 2024 into a standardized, indexed structure.\n"
        "2. High-Speed Spatial & Temporal Indexing: Enables instant proximity queries (within km radius of any global city) with PostGIS spatial indexes and in-memory spatial geokeys.\n"
        "3. Triple-Task Machine Learning: Provides automated categorization of water body type (Task 1), automated assessment of water quality grade (Task 2), and 10-year future trend prediction (Task 3)."
    )

    # ── Section 3: System Architecture Diagram ──
    h3 = doc.add_heading("3. Full-Stack System Architecture", level=1)
    doc.add_paragraph(
        "The architecture is organized into four distinct tiers: Data Ingestion, Storage & Indexing Engine, "
        "FastAPI Backend & ML Services, and the React 18 / Vite Presentation Studio."
    )
    arch_img_path = create_architecture_diagram()
    doc.add_picture(str(arch_img_path), width=Inches(6.8))
    doc.add_paragraph("Figure 1: BlueSage Tiered System Architecture and Dual Execution Model.").alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # ── Section 4: Data Engineering & Metrics ──
    h4 = doc.add_heading("4. Verified Scientific Data Sources & Environmental Features", level=1)
    doc.add_paragraph(
        "BlueSage strictly avoids synthetic artifacts: every observation derives from verified scientific remote sensing datasets "
        "and international hydrological monitoring networks:"
    )

    t_src = doc.add_table(rows=5, cols=4)
    t_src.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_src_headers = ["Source Repository", "Institution", "Key Provided Metrics", "Access Protocol"]
    for j, h in enumerate(t_src_headers):
        t_src.cell(0, j).paragraphs[0].text = h

    src_rows = [
        ("HydroLAKES v1.0", "McGill University & WWF", "Global lake/reservoir registry, centroids (lat/lon), surface area (km²), shoreline, depth", "ArcGIS REST API / Open DB"),
        ("JRC Global Surface Water", "European Commission JRC", "38-year Landsat satellite observations: water occurrence %, monthly seasonality (mo/yr)", "Nature Research Archive"),
        ("USGS Water Quality Portal", "USGS & US EPA", "In-situ monitoring: pH level, Dissolved Oxygen (DO mg/L), Turbidity (NTU), Chlorophyll-a (µg/L)", "Free REST API (/data/Result)"),
        ("OpenStreetMap Nominatim", "OpenStreetMap Foundation", "City-to-coordinate geocoding & bounding box extraction for global viewport navigation", "Open Nominatim REST API")
    ]
    for i, row in enumerate(src_rows, start=1):
        for j, val in enumerate(row):
            t_src.cell(i, j).paragraphs[0].text = val
    style_table(t_src, header_bg="047857")

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Explanation of features
    doc.add_heading("Key Remote Sensing & Chemical Metrics Explained:", level=2)
    doc.add_paragraph(
        "• NDWI (Normalized Difference Water Index): Derived from Green and NIR bands (Green - NIR) / (Green + NIR). Values > 0 indicate open water; higher positive values reflect deeper, clearer water.\n"
        "• Water Occurrence (%): Percentage of months throughout the year where satellite sensors confirmed the presence of surface water.\n"
        "• Seasonality (months/year): The permanent vs ephemeral nature of the water body (e.g. 12 = perennial lake, 4-6 = monsoon wetland).\n"
        "• Dissolved Oxygen (DO, mg/L): Healthy freshwater requires > 5.0 mg/L; levels below 3.0 mg/L indicate hypoxia dangerous to aquatic life.\n"
        "• Turbidity (NTU): Measures water cloudiness caused by suspended sediments and algae. Low values (< 5 NTU) indicate clear water.\n"
        "• pH Level: Safe freshwater ranges between 6.5 and 8.5. Extreme acidification or alkalinization indicates severe contamination."
    )

    # ── Section 5: Machine Learning Triple-Task Engine ──
    h5 = doc.add_heading("5. Triple-Task Machine Learning Engine", level=1)
    doc.add_paragraph(
        "BlueSage implements three distinct machine learning components that transform historical temporal measurements into actionable environmental classifications and decadal forecasts:"
    )

    ml_img_path = create_ml_diagram()
    doc.add_picture(str(ml_img_path), width=Inches(6.8))
    doc.add_paragraph("Figure 2: Triple-Task ML Pipeline — Features, Models, and Target Outputs.").alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    t_ml = doc.add_table(rows=4, cols=5)
    t_ml.alignment = WD_TABLE_ALIGNMENT.CENTER
    ml_headers = ["Task ID", "ML Objective", "Model Algorithm", "Key Features Used", "Performance"]
    for j, h in enumerate(ml_headers):
        t_ml.cell(0, j).paragraphs[0].text = h

    ml_rows = [
        ("Task 1", "Water Body Type Classification", "RandomForestClassifier (150 trees)", "Area (km²), Occurrence %, Seasonality, NDWI", "~90% Test Accuracy"),
        ("Task 2", "Water Quality Classification", "RandomForestClassifier (200 trees)", "pH, DO, Turbidity, Chlorophyll-a, NDWI, Area", "~94% Test Accuracy (F1: 0.907)"),
        ("Task 3", "Decadal Future Prediction", "Polynomial Regression (d=2) + Trajectory", "10-Year historical area, NDWI & status series", "Per-WB Model (10-Yr Horizon)")
    ]
    for i, row in enumerate(ml_rows, start=1):
        for j, val in enumerate(row):
            t_ml.cell(i, j).paragraphs[0].text = val
    style_table(t_ml, header_bg="B45309")

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    doc.add_heading("Task Details & Scientific Output:", level=2)
    doc.add_paragraph(
        "1. Task 1 (Type Classification): Accurately distinguishes between Lake, Pond, Reservoir, Wetland, and River based on area scale, seasonal consistency, and surface reflectance.\n"
        "2. Task 2 (Quality Grading): Evaluates ecological safety into five standardized tiers: Excellent (Score 80–100), Good (60–80), Fair (40–60), Poor (20–40), and Critical (< 20).\n"
        "3. Task 3 (Future Change): Calculates regression slope trajectories over 10 historical years to categorize decadal fates: Expand, Stable, Shrink, or Disappear, projecting exact surface areas through 2034."
    )

    # ── Section 6: Database & Indexing Strategy ──
    h6 = doc.add_heading("6. Spatial Indexing & Dual Execution Strategy", level=1)
    doc.add_paragraph(
        "A standout architectural strength of BlueSage is its dual execution model: it supports full production-grade PostGIS spatial indexing, "
        "while providing an instant zero-configuration offline fallback so that anyone can run the app without installing PostgreSQL."
    )

    t_idx = doc.add_table(rows=7, cols=3)
    t_idx.alignment = WD_TABLE_ALIGNMENT.CENTER
    idx_headers = ["Index Identifier", "Technology / Engine", "Target Use Case & Performance Impact"]
    for j, h in enumerate(idx_headers):
        t_idx.cell(0, j).paragraphs[0].text = h

    idx_rows = [
        ("idx_wb_centroid_gist", "PostGIS GiST (R-Tree variant)", "Sub-millisecond bounding box and radius queries (ST_DWithin, ST_MakeEnvelope)."),
        ("idx_wb_country_type", "PostgreSQL B-Tree", "Composite index accelerating multi-attribute filtering by country and water body type."),
        ("idx_obs_wb_year", "PostgreSQL B-Tree", "Fast temporal joins connecting master records with 10 years of annual observation rows."),
        ("idx_obs_year_ndwi", "PostgreSQL B-Tree", "Optimizes range scans on satellite index thresholds across observation years."),
        ("idx_wb_name_trgm", "GIN Trigram Extension", "Tolerant fuzzy text search allowing users to find water bodies even with typos."),
        ("spatial_grid_index", "Discrete Geokey (GEO_LAT_LON)", "Used during offline fallback for instant O(1) in-memory bucketed spatial retrieval.")
    ]
    for i, row in enumerate(idx_rows, start=1):
        for j, val in enumerate(row):
            t_idx.cell(i, j).paragraphs[0].text = val
    style_table(t_idx, header_bg="475569")

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # ── Section 7: Frontend & Map Visualization ──
    h7 = doc.add_heading("7. Frontend Studio & Map Visualization Features", level=1)
    doc.add_paragraph(
        "The user interface is built with React 18, Tailwind CSS, Leaflet, and Recharts, providing an intuitive, interactive experience:"
    )
    doc.add_paragraph(
        "• Multi-Layer Map Studio: Includes a top-right layer control toggling between 5 free tile layers:\n"
        "    - 🗺️ Street View (OpenStreetMap)\n"
        "    - 🛰️ Satellite Imagery (Esri World Imagery)\n"
        "    - 🏔️ Topographic Terrain (OpenTopoMap)\n"
        "    - 🌙 Dark Mode (CartoDB Dark Matter)\n"
        "    - 🤍 Minimal Light Mode (CartoDB Positron)\n"
        "  All layers operate with zero API keys and zero billing requirements.\n"
        "• Instant Marker Sync: Clicking any water body circle marker on the map instantly synchronizes the right-hand panel, updating details, historical metrics, and classification options.\n"
        "• Interactive Classification Panel: Dual tabs for Task 1 and Task 2. Probability distribution bars are fixed in a consistent order with smooth CSS animations when switching between water bodies.\n"
        "• 10-Year Decadal Charts: Renders historical measurements (solid line) seamlessly merging into 10-year ML forecasts (dashed line) for NDWI, Area, and Quality scores.\n"
        "• One-Click Dataset Export: Direct header and dashboard buttons to download the 1,650-row indexed temporal dataset (`indexed_waterbody_dataset.csv`)."
    )

    # ── Section 8: REST API Reference ──
    h8 = doc.add_heading("8. Complete REST API Reference", level=1)
    doc.add_paragraph("All API endpoints are documented interactively via Swagger UI at http://127.0.0.1:8000/docs.")

    t_api = doc.add_table(rows=9, cols=3)
    t_api.alignment = WD_TABLE_ALIGNMENT.CENTER
    api_headers = ["HTTP Method & Route", "Query / Payload Parameters", "Description & Response"]
    for j, h in enumerate(api_headers):
        t_api.cell(0, j).paragraphs[0].text = h

    api_rows = [
        ("GET /api/waterbodies/", "country, city, type, quality, limit, offset", "List and filter water bodies across the global registry."),
        ("GET /api/waterbodies/near", "lat, lon, radius_km (default 200), limit", "Finds nearby water bodies sorted by haversine distance."),
        ("GET /api/waterbodies/bbox", "min_lat, max_lat, min_lon, max_lon, limit", "Retrieves water bodies falling within a geographic bounding box."),
        ("GET /api/waterbodies/{id}", "id (integer)", "Full water body detail with 10-year observations and future predictions."),
        ("GET /api/waterbodies/{id}/observations", "start_year, end_year", "Time-series annual observations (2014–2024) for a given water body."),
        ("GET /api/waterbodies/export-csv", "None", "Direct download of the complete 1,650-record indexed CSV dataset."),
        ("POST /api/classify/body-type", "area_sq_km, ndwi, occurrence, seasonality", "Task 1: Predicts water body type with class probabilities."),
        ("POST /api/classify/", "pH, DO, turbidity, chlorophyll-a, NDWI, area...", "Task 2: Predicts water quality grade and confidence score.")
    ]
    for i, row in enumerate(api_rows, start=1):
        for j, val in enumerate(row):
            t_api.cell(i, j).paragraphs[0].text = val
    style_table(t_api, header_bg="6B21A8")

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # ── Section 9: New Member Onboarding & Developer Guide ──
    h9 = doc.add_heading("9. New Member Onboarding & Developer Runbook", level=1)
    doc.add_paragraph(
        "Welcome to the BlueSage team! Follow these simple steps to set up and run the project locally within 2 minutes."
    )

    doc.add_heading("Step 1: Clone the Repository", level=2)
    doc.add_paragraph("git clone https://github.com/Souvagya06/BlueSage.git\ncd BlueSage")

    doc.add_heading("Step 2: Start the Application (Zero-Config Fast Start)", level=2)
    doc.add_paragraph(
        "You do NOT need PostgreSQL installed to run the application! BlueSage includes an auto-bootstrapper in backend/main.py "
        "that automatically detects and runs your virtual environment:\n\n"
        "cd backend\n"
        "python main.py\n\n"
        "The server will start at http://127.0.0.1:8000. Open this URL in your browser to access the complete frontend dashboard and interactive map!"
    )

    doc.add_heading("Step 3: Setting Up a Fresh Virtual Environment (If Needed)", level=2)
    doc.add_paragraph(
        "If you are setting up the Python environment on a new machine:\n"
        "1. cd backend\n"
        "2. python -m venv venv\n"
        "3. Windows PowerShell: .\\venv\\Scripts\\Activate.ps1   (or activate.bat in CMD)\n"
        "   Mac/Linux: source venv/bin/activate\n"
        "4. pip install -r requirements.txt\n"
        "5. python main.py"
    )

    doc.add_heading("Step 4: Making Changes to the Frontend", level=2)
    doc.add_paragraph(
        "The frontend is located in the frontend/ directory (React 18 + Vite). After editing any JSX or CSS files in frontend/src/:\n"
        "1. cd frontend\n"
        "2. npm install         (first time only)\n"
        "3. npm run build       (builds into frontend/dist, which FastAPI serves directly!)\n"
        "4. Refresh your browser at http://127.0.0.1:8000"
    )

    doc.add_heading("Step 5: Retraining Machine Learning Models (Optional)", level=2)
    doc.add_paragraph(
        "If you update the dataset in data/processed/ and want to re-train the models:\n"
        "• Train Quality Classifier (Task 2): python ml/train_classifier.py\n"
        "• Train Body Type Classifier (Task 1): python ml/train_body_type_classifier.py\n"
        "• Train Future Predictor (Task 3): python ml/train_predictor.py\n"
        "All trained artifacts are automatically saved into backend/ml/models/."
    )

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # ── Section 10: Troubleshooting FAQ ──
    h10 = doc.add_heading("10. Troubleshooting FAQ for New Members", level=1)
    doc.add_paragraph(
        "Q1: I see 'WARNING: Could not connect to PostgreSQL on startup' in the terminal. Is this an error?\n"
        "A: No, this is completely normal and expected! BlueSage is designed to run seamlessly offline. It detected that PostgreSQL isn't running and automatically loaded the full 150 water body indexed dataset from CSV into memory. Everything works at 100% functionality.\n\n"
        "Q2: Windows PowerShell gives an error: 'running scripts is disabled on this system'.\n"
        "A: Run this command in PowerShell once to allow script execution for your session:\n"
        "   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass\n"
        "   .\\venv\\Scripts\\Activate.ps1\n\n"
        "Q3: I updated a file in frontend/src/ but don't see the changes on http://127.0.0.1:8000.\n"
        "A: Run `npm --prefix frontend run build` to compile your React changes into `frontend/dist/`, then restart `python main.py`."
    )

    # Save
    doc.save(str(DOC_PATH))
    print(f"SUCCESS: Document created at {DOC_PATH}")

if __name__ == "__main__":
    build_document()

