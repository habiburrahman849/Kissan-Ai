from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import User, FarmEvent, Memory


class MemoryEngine:
    def recall_memories(self, db: Session, user_id: str, query: str, limit: int = 5) -> list[str]:
        """
        Recall relevant memories for a user based on keyword matching (offline) or listing.
        """
        memories = db.query(Memory).filter(Memory.user_id == user_id).order_by(
            Memory.importance.desc(), Memory.last_accessed.desc()
        ).limit(limit).all()

        results = []
        for m in memories:
            m.last_accessed = func.now()
            m.access_count += 1
            results.append(f"[{m.category or 'General'}] {m.content}")
        db.commit()
        return results

    def store_memory(
        self,
        db: Session,
        user_id: str,
        content: str,
        category: str = "general",
        memory_type: str = "general",
        importance: int = 5
    ) -> Memory:
        """
        Store a new memory in the database.
        """
        # Clean duplicate memories
        existing = db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.content == content
        ).first()
        if existing:
            existing.last_accessed = func.now()
            existing.access_count += 1
            db.commit()
            return existing

        new_mem = Memory(
            user_id=user_id,
            memory_type=memory_type,
            category=category,
            content=content,
            importance=importance,
            source="conversation",
            created_at=func.now(),
            last_accessed=func.now(),
            access_count=1
        )
        db.add(new_mem)
        db.commit()
        db.refresh(new_mem)
        return new_mem

    def get_profile_context(self, db: Session, user_id: str) -> str:
        """
        Synthesizes profile, events, and memories into a prompt context block.
        """
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return "No profile context found."

        # Profile context
        context = f"--- FARMER IDENTITY & PROFILE ---\n"
        context += f"Name: {user.full_name or 'Guest Farmer'}\n"
        if user.location_district:
            context += f"District: {user.location_district}\n"
        if user.location_tehsil:
            context += f"Tehsil: {user.location_tehsil}\n"
        if user.land_size_acres:
            context += f"Land Size: {user.land_size_acres} Acres\n"
        if user.soil_type:
            context += f"Soil Type: {user.soil_type}\n"
        context += f"Preferred Language: {user.preferred_language or 'hinglish'}\n"
        context += f"Account Status: {'Guest' if user.is_guest else 'Registered User'}\n\n"

        # Recent farm events
        events = db.query(FarmEvent).filter(FarmEvent.user_id == user_id).order_by(
            FarmEvent.event_date.desc()
        ).limit(3).all()

        if events:
            context += "--- RECENT FARM EVENTS ---\n"
            for ev in events:
                date_str = ev.event_date.strftime("%Y-%m-%d") if ev.event_date else "Unknown Date"
                context += f"- [{date_str}] {ev.event_type} on {ev.crop_name or 'crops'} ({ev.crop_variety or 'variety'}): {ev.details or ''} (Outcome: {ev.outcome or 'pending'})\n"
            context += "\n"

        # Memories context
        memories = db.query(Memory).filter(Memory.user_id == user_id).order_by(
            Memory.importance.desc()
        ).limit(5).all()

        if memories:
            context += "--- PERSISTENT MEMORY CONTEXT ---\n"
            for mem in memories:
                context += f"- [{mem.category or 'General'}] {mem.content}\n"
            context += "\n"

        return context
