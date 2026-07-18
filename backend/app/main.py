from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import chat, crops, documents, farmers, health, weather
from app.config import get_settings
from app.db.session import init_db

settings = get_settings()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(farmers.router, prefix="/api")
app.include_router(crops.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(weather.router, prefix="/api")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


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
    requested = (frontend_path / page_name).resolve()
    if frontend_path in requested.parents and requested.is_file():
        return FileResponse(requested)
    fallback = frontend_path / "index.html"
    if fallback.exists():
        return FileResponse(fallback)
    return {"message": "Kissan AI backend is running"}
