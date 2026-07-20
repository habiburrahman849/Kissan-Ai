"""
Kissan AI — FastAPI entry point (local + Render).

Static frontend lives in repo `static/` (HTML/CSS/JS).
API routes are under `/api/*`. Non-API paths serve the SPA files.
"""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import auth, chat, health, weather
from app.config import get_settings
from app.db import init_db

settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0")

# ── CORS: allow all origins (hackathon / same-origin SPA also works) ─────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API routers ──────────────────────────────────────────────────────────────
app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(weather.router, prefix="/api")


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    static_dir = settings.frontend_path.resolve()
    print(f"Kissan AI starting | env={settings.environment} | static={static_dir} exists={static_dir.exists()}")


# Ensure DB tables exist even if lifespan/startup order varies
init_db()

# Resolved path to repo `static/` (or FRONTEND_DIR override)
STATIC_DIR: Path = settings.frontend_path.resolve()


def _safe_static_file(relative: str) -> Path | None:
    """Return an absolute file path inside STATIC_DIR, or None if missing/unsafe."""
    if not STATIC_DIR.exists():
        return None
    # Normalize and block path traversal
    candidate = (STATIC_DIR / relative).resolve()
    try:
        candidate.relative_to(STATIC_DIR)
    except ValueError:
        return None
    if candidate.is_file():
        return candidate
    return None


# Also expose assets under /static/* (mirrors folder name; optional convenience)
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static_assets")


@app.get("/")
def serve_index():
    index = _safe_static_file("index.html")
    if index:
        return FileResponse(index)
    return JSONResponse(
        {
            "message": "Kissan AI backend is running",
            "health": "/api/health",
            "hint": "Place frontend files in static/ (FRONTEND_DIR)",
        }
    )


@app.get("/{page_name:path}")
def serve_page(page_name: str):
    """Serve HTML/CSS/JS from static/ so relative links (shared.js, chat.html) work."""
    # Never intercept API (routers already claim /api/*, but be defensive)
    if not page_name or page_name == "api" or page_name.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not found")

    # Direct file: chat.html, shared.js, shared.css, architecture_diagram.svg
    direct = _safe_static_file(page_name)
    if direct:
        return FileResponse(direct)

    # Extensionless: /chat → chat.html
    if "." not in Path(page_name).name:
        html = _safe_static_file(f"{page_name}.html")
        if html:
            return FileResponse(html)

    # SPA-style fallback
    index = _safe_static_file("index.html")
    if index:
        return FileResponse(index)

    raise HTTPException(status_code=404, detail="Page not found")


if __name__ == "__main__":
    # Render sets PORT; local default 8000
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=os.environ.get("ENVIRONMENT", "development").lower()
        in {"development", "dev", "local"},
    )
