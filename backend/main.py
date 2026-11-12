"""
FastAPI main application entry point.

Run directly (any Python — auto-switches to venv):
    python main.py                      # from inside backend/
    python main.py --port 8080          # custom port
    python main.py --host 0.0.0.0       # expose on network
"""
import os
import sys
import argparse
from pathlib import Path

# ─── Auto-bootstrap: re-launch with venv Python if not already inside it ──────
_HERE = Path(__file__).resolve().parent                # backend/
_VENV_PYTHON = _HERE / "venv" / "Scripts" / "python.exe"  # Windows venv

def _in_venv() -> bool:
    """Return True if the current interpreter lives inside our backend/venv."""
    try:
        return Path(sys.executable).resolve().is_relative_to(_VENV_PYTHON.parent)
    except AttributeError:
        # Python < 3.9 fallback
        return str(_VENV_PYTHON.parent) in str(Path(sys.executable).resolve())

if not _in_venv() and _VENV_PYTHON.exists():
    # Re-exec this script with the venv interpreter — passes all CLI args through
    import subprocess
    result = subprocess.run([str(_VENV_PYTHON), __file__] + sys.argv[1:])
    sys.exit(result.returncode)
elif not _in_venv() and not _VENV_PYTHON.exists():
    print("⚠️  WARNING: venv not found at backend/venv/. Using system Python.")
    print("   If you get import errors, run:  pip install -r requirements.txt")
    print()
# ──────────────────────────────────────────────────────────────────────────────

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from database import engine, Base
from routers import waterbodies, classification, prediction
import models.waterbody  # ensure models are registered


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Attempt to create tables on startup if database is accessible
    try:
        Base.metadata.create_all(bind=engine)
        print("INFO: Database connected and tables verified.")
    except Exception as e:
        print(f"WARNING: Could not connect to PostgreSQL on startup: {e}")
        print("WARNING: The frontend and mock/static endpoints will still work, but DB queries will fail until PostgreSQL is running.")
    yield


app = FastAPI(
    title="Temporal Water-Body Dataset API",
    description=(
        "API for querying a 5–10 year temporal dataset of global water bodies. "
        "Supports spatial/attribute-indexed retrieval, ML classification, and future prediction."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ─── CORS (allow React dev server) ────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(waterbodies.router)
app.include_router(classification.router)
app.include_router(prediction.router)


@app.get("/health")
def health():
    return {"status": "ok"}


# ─── Serve Frontend SPA if built ──────────────────────────────────────────────
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    # Mount static assets
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    # Catch-all for SPA routes (e.g. /, /explore, /predict)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")
else:
    @app.get("/")
    def root():
        return {
            "message": "Temporal Water-Body Dataset API",
            "docs": "/docs",
            "version": "1.0.0",
        }


# ─── Entry point: python main.py ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    parser = argparse.ArgumentParser(description="BlueSage — Water Body Monitoring API")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    parser.add_argument("--reload", action="store_true", default=True, help="Enable auto-reload on code change")
    parser.add_argument("--no-reload", dest="reload", action="store_false", help="Disable auto-reload")
    args = parser.parse_args()

    print("=" * 60)
    print("  🌊  BlueSage — Water Body Monitoring Platform")
    print("=" * 60)
    print(f"  API  : http://{args.host}:{args.port}/docs")
    print(f"  App  : http://{args.host}:{args.port}/")
    print(f"  Reload: {'enabled' if args.reload else 'disabled'}")
    print("  Press Ctrl+C to stop")
    print("=" * 60)

    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        reload_dirs=[str(Path(__file__).parent)],  # watch only backend/
    )


