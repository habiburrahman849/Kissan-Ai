from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings


settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url_resolved.startswith("sqlite") else {}

engine = create_engine(settings.database_url_resolved, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _migrate_sqlite() -> None:
    """Add new columns to existing SQLite DBs without dropping data."""
    if not settings.database_url_resolved.startswith("sqlite"):
        return
    with engine.begin() as conn:
        rows = conn.execute(text("PRAGMA table_info(farmers)")).fetchall()
        if not rows:
            return
        existing = {row[1] for row in rows}
        alters = []
        if "google_id" not in existing:
            alters.append("ALTER TABLE farmers ADD COLUMN google_id VARCHAR(128)")
        if "clerk_id" not in existing:
            alters.append("ALTER TABLE farmers ADD COLUMN clerk_id VARCHAR(128)")
        if "avatar_url" not in existing:
            alters.append("ALTER TABLE farmers ADD COLUMN avatar_url VARCHAR(500)")
        if "is_guest" not in existing:
            alters.append("ALTER TABLE farmers ADD COLUMN is_guest BOOLEAN DEFAULT 1")
        if "password_hash" not in existing:
            alters.append("ALTER TABLE farmers ADD COLUMN password_hash VARCHAR(256)")
        if "converted_from_guest_id" not in existing:
            alters.append("ALTER TABLE farmers ADD COLUMN converted_from_guest_id INTEGER")
        for sql in alters:
            conn.execute(text(sql))


def init_db() -> None:
    from app.db import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    try:
        _migrate_sqlite()
    except Exception as exc:
        print(f"DB migrate warning: {exc}")
