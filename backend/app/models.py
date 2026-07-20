from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(120), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=True)
    password_hash = Column(String(256), nullable=True)
    full_name = Column(String(120), nullable=True)
    location_district = Column(String(120), nullable=True)
    location_tehsil = Column(String(120), nullable=True)
    land_size_acres = Column(String(120), nullable=True)
    soil_type = Column(String(120), nullable=True)
    preferred_language = Column(String(50), default="hinglish")
    is_guest = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(120), ForeignKey("users.user_id"), nullable=False)
    session_id = Column(String(120), nullable=False)
    role = Column(String(40), nullable=False)  # user or assistant
    content = Column(Text, nullable=False)
    language = Column(String(40), nullable=True)
    timestamp = Column(DateTime, default=func.now())


class FarmEvent(Base):
    __tablename__ = "farm_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(120), ForeignKey("users.user_id"), nullable=False)
    event_type = Column(String(120), nullable=False)
    crop_name = Column(String(120), nullable=True)
    crop_variety = Column(String(120), nullable=True)
    event_date = Column(DateTime, default=func.now())
    details = Column(Text, nullable=True)
    outcome = Column(String(120), default="pending")


class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(120), ForeignKey("users.user_id"), nullable=False)
    memory_type = Column(String(120), nullable=True)
    category = Column(String(120), nullable=True)
    content = Column(Text, nullable=False)
    importance = Column(Integer, default=5)
    source = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=func.now())
    last_accessed = Column(DateTime, default=func.now())
    access_count = Column(Integer, default=1)
