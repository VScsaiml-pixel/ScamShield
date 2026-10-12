import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import settings
from app.database import engine, Base, init_db
import app.models  # ensure models are registered
from app.api import api_router

# Path to frontend build directory for unified single-port hosting
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")
ASSETS_DIR = os.path.join(FRONTEND_DIST, "assets")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create SQLite database tables & apply schema upgrades
    init_db()
    yield
    # Shutdown logic (if any)


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Scam & Phishing Detection Platform API (College Mini Project)",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration to allow local frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list + [
        "http://localhost:5173", 
        "http://127.0.0.1:5173", 
        "http://localhost:8000", 
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all API routes under /api
app.include_router(api_router)

# Mount static frontend assets if built
if os.path.exists(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")


# Unified single-port hosting: serve React SPA at root
@app.get("/")
async def serve_root():
    index_html = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(index_html):
        return FileResponse(index_html)
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "documentation": "/docs",
        "health_check": "/api/health",
        "version": "1.0.0",
        "status": "online"
    }


# Fallback for SPA routing and static root files (e.g. vite.svg, favicon)
@app.get("/{full_path:path}")
async def serve_spa_fallback(full_path: str):
    # Never intercept backend routes
    if full_path.startswith("api") or full_path.startswith("docs") or full_path in ["openapi.json", "redoc"]:
        raise HTTPException(status_code=404, detail="Not Found")

    # Serve static root files if present (e.g., vite.svg)
    requested_file = os.path.join(FRONTEND_DIST, full_path)
    if os.path.exists(requested_file) and os.path.isfile(requested_file):
        return FileResponse(requested_file)

    # Return index.html for SPA routing
    index_html = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(index_html):
        return FileResponse(index_html)

    raise HTTPException(status_code=404, detail="Frontend build not found.")
