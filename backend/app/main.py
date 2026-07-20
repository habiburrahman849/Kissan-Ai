from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import auth, chat, health, weather
from app.config import get_settings
from app.db import init_db

settings = get_settings()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(weather.router, prefix="/api")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


# Initialize DB immediately
init_db()

frontend_path = settings.frontend_path.resolve()
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")


@app.get("/")
def serve_index():
    index = frontend_path / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"message": "Kissan AI backend is running"}


@app.get("/{page_name:path}")
def serve_page(page_name: str):
    # Ignore /api queries
    if page_name.startswith("api"):
        return None
    requested = (frontend_path / page_name).resolve()
    # Guard to prevent directory traversal
    if frontend_path in requested.parents and requested.is_file():
        return FileResponse(requested)
    # Check if page_name has extension. If not, try appending .html
    if not requested.suffix:
        html_file = (frontend_path / f"{page_name}.html").resolve()
        if frontend_path in html_file.parents and html_file.is_file():
            return FileResponse(html_file)
    fallback = frontend_path / "index.html"
    if fallback.exists():
        return FileResponse(fallback)
    return {"message": "Kissan AI backend is running"}
