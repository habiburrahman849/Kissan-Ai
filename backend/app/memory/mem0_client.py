from __future__ import annotations

from datetime import datetime

import httpx
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models import CropCycle, FarmEvent, Farmer


class Mem0Client:
    """Local-first memory facade; swap internals with hosted Mem0 when keys exist."""

    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def cloud_enabled(self) -> bool:
        return bool(self.settings.mem0_api_key)

    def _cloud_headers(self) -> dict:
        return {
            "Authorization": f"Token {self.settings.mem0_api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _user_id(self, farmer_id: int) -> str:
        return f"farmer_{farmer_id}"

    def ensure_farmer(self, db: Session, farmer_id: int) -> Farmer:
        farmer = db.get(Farmer, farmer_id)
        if farmer:
            return farmer
        farmer = Farmer(id=farmer_id, name="Guest Farmer", is_guest=True)
        db.add(farmer)
        db.commit()
        db.refresh(farmer)
        return farmer

    def get_profile(self, db: Session, farmer_id: int) -> dict:
        farmer = self.ensure_farmer(db, farmer_id)
        active_crop = (
            db.query(CropCycle)
            .filter(CropCycle.farmer_id == farmer.id, CropCycle.status == "active")
            .order_by(CropCycle.created_at.desc())
            .first()
        )
        events = (
            db.query(FarmEvent)
            .filter(FarmEvent.farmer_id == farmer.id)
            .order_by(FarmEvent.created_at.desc())
            .limit(8)
            .all()
        )
        return {
            "farmer_name": farmer.name,
            "district": farmer.district,
            "village": farmer.village,
            "preferred_language": farmer.preferred_language,
            "phone": farmer.phone,
            "email": farmer.email,
            "land_size": farmer.land_size,
            "primary_crops": farmer.primary_crops,
            "soil_type": farmer.soil_type,
            "irrigation": farmer.irrigation,
            "farming_type": farmer.farming_type,
            "current_crop": active_crop.crop_name if active_crop else None,
            "sowing_date": active_crop.sowing_date if active_crop else None,
            "crop_cycle_id": active_crop.id if active_crop else None,
            "recent_events": [
                {"type": event.event_type, "description": event.description, "date": event.event_date}
                for event in events
            ],
        }

    async def search_cloud_memories(self, farmer_id: int, query: str, limit: int = 6) -> list[dict]:
        if not self.cloud_enabled:
            return []
        try:
            async with httpx.AsyncClient(timeout=12) as client:
                response = await client.post(
                    f"{self.settings.mem0_api_base.rstrip('/')}/v3/memories/search/",
                    headers=self._cloud_headers(),
                    json={
                        "query": query,
                        "filters": {"user_id": self._user_id(farmer_id)},
                        "top_k": limit,
                        "threshold": 0.05,
                    },
                )
                response.raise_for_status()
                results = response.json().get("results", [])
                return [
                    {
                        "memory": item.get("memory"),
                        "score": item.get("score"),
                        "categories": item.get("categories", []),
                        "created_at": item.get("created_at"),
                    }
                    for item in results
                    if item.get("memory")
                ]
        except Exception:
            return []

    async def add_cloud_conversation(self, farmer_id: int, user_message: str, assistant_message: str) -> None:
        if not self.cloud_enabled:
            return
        try:
            async with httpx.AsyncClient(timeout=12) as client:
                await client.post(
                    f"{self.settings.mem0_api_base.rstrip('/')}/v3/memories/add/",
                    headers=self._cloud_headers(),
                    json={
                        "user_id": self._user_id(farmer_id),
                        "messages": [
                            {"role": "user", "content": user_message},
                            {"role": "assistant", "content": assistant_message},
                        ],
                        "metadata": {"app": "kissan-ai", "channel": "website"},
                    },
                )
        except Exception:
            return

    def apply_facts(self, db: Session, farmer_id: int, facts: dict, raw_message: str) -> None:
        farmer = self.ensure_farmer(db, farmer_id)
        
        # 1. Update farmer profile fields if present in facts
        name = facts.get("name") or facts.get("farmer_name")
        if name:
            farmer.name = name
        if facts.get("district"):
            farmer.district = facts.get("district")
        if facts.get("village"):
            farmer.village = facts.get("village")
        if facts.get("land_size"):
            farmer.land_size = facts.get("land_size")
        if facts.get("primary_crops"):
            farmer.primary_crops = facts.get("primary_crops")
        if facts.get("soil_type"):
            farmer.soil_type = facts.get("soil_type")
        if facts.get("irrigation"):
            farmer.irrigation = facts.get("irrigation")
        if facts.get("farming_type"):
            farmer.farming_type = facts.get("farming_type")
        if name or facts.get("district") or facts.get("village") or facts.get("land_size") or facts.get("primary_crops") or facts.get("soil_type") or facts.get("irrigation") or facts.get("farming_type"):
            farmer.is_guest = False # They filled some details now
            
        if facts.get("season_status") == "harvested":
            self.archive_active_crop(db, farmer.id)
            db.add(FarmEvent(farmer_id=farmer.id, event_type="harvest", description=raw_message))
            db.commit()
            return

        active_crop = (
            db.query(CropCycle)
            .filter(CropCycle.farmer_id == farmer.id, CropCycle.status == "active")
            .order_by(CropCycle.created_at.desc())
            .first()
        )
        if facts.get("current_crop"):
            if not active_crop:
                active_crop = CropCycle(farmer_id=farmer.id, crop_name=facts["current_crop"])
                db.add(active_crop)
                db.flush()
            elif active_crop.crop_name != facts["current_crop"]:
                active_crop.crop_name = facts["current_crop"]

        # 2. Update crop cycle details if present
        if active_crop:
            if facts.get("variety"):
                active_crop.variety = facts.get("variety")
            if facts.get("sowing_date"):
                active_crop.sowing_date = facts.get("sowing_date")

        event_type = "observation"
        if facts.get("last_fertilizer"):
            event_type = "fertilizer"
        elif facts.get("recent_symptoms"):
            event_type = "symptom"

        if facts:
            db.add(
                FarmEvent(
                    farmer_id=farmer.id,
                    crop_cycle_id=active_crop.id if active_crop else None,
                    event_type=event_type,
                    description=raw_message,
                )
            )
            db.commit()

    def archive_active_crop(self, db: Session, farmer_id: int) -> None:
        active_crops = db.query(CropCycle).filter(CropCycle.farmer_id == farmer_id, CropCycle.status == "active").all()
        for crop in active_crops:
            crop.status = "archived"
            crop.archived_at = datetime.utcnow()
        db.commit()
