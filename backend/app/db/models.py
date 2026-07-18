from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), default="Ahmad")
    district = Column(String(120), nullable=True)
    village = Column(String(120), nullable=True)
    preferred_language = Column(String(20), default="ur")
    phone = Column(String(40), default="+92 300 1234567")
    email = Column(String(120), default="ahmad@kissan.ai")
    land_size = Column(String(80), default="5.2 Acres")
    primary_crops = Column(String(240), default="Wheat, Cotton, Rice")
    soil_type = Column(String(120), default="Sandy Loam")
    irrigation = Column(String(80), default="Canal & Tube Well")
    farming_type = Column(String(80), default="Organic")
    created_at = Column(DateTime, default=datetime.utcnow)

    crop_cycles = relationship("CropCycle", back_populates="farmer")


class CropCycle(Base):
    __tablename__ = "crop_cycles"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"))
    crop_name = Column(String(120))
    variety = Column(String(120), nullable=True)
    sowing_date = Column(String(40), nullable=True)
    status = Column(String(40), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    archived_at = Column(DateTime, nullable=True)

    farmer = relationship("Farmer", back_populates="crop_cycles")


class FarmEvent(Base):
    __tablename__ = "farm_events"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"))
    crop_cycle_id = Column(Integer, ForeignKey("crop_cycles.id"), nullable=True)
    event_type = Column(String(80))
    description = Column(Text)
    event_date = Column(String(40), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"))
    role = Column(String(20))
    content = Column(Text)
    language = Column(String(20), default="ur")
    created_at = Column(DateTime, default=datetime.utcnow)


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(240))
    source = Column(String(240), nullable=True)
    crop = Column(String(120), nullable=True)
    region = Column(String(120), nullable=True)
    file_path = Column(String(500))
    status = Column(String(40), default="uploaded")
    uploaded_at = Column(DateTime, default=datetime.utcnow)
