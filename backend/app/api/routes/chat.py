from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User, Conversation, FarmEvent, Memory
from app.core.auth import get_optional_user
from app.language_detector import detect_language
from app.qwen_client import QwenClient
from app.memory_engine import MemoryEngine
from app.agents import AgentOrchestrator

router = APIRouter(prefix="/chat", tags=["chat"])

# Global clients/engines
qwen_client = QwenClient()
memory_engine = MemoryEngine()
orchestrator = AgentOrchestrator()


class ChatMessageRequest(BaseModel):
    message: str
    session_id: str | None = "default_session"
    user_id: str | None = None
    language: str | None = None


class ChatMessageResponse(BaseModel):
    response: str
    language: str
    session_id: str
    agents_used: list[str]
    memory_recall: list[str]
    confidence: float


def _extract_and_update_profile(db: Session, user: User, message: str):
    """
    Parse message and update SQLite User record with new farming attributes.
    """
    msg = message.lower()
    
    # 1. District detection
    districts = ["multan", "faisalabad", "lahore", "sahiwal", "khanewal", "sargodha", "larkana", "hyderabad", "peshawar", "quetta"]
    for d in districts:
        if d in msg:
            user.location_district = d.capitalize()
            memory_engine.store_memory(db, user.user_id, f"Farmer resides in district {d.capitalize()}", category="location")
            break

    # 2. Soil detection
    soils = ["sandy", "clay", "loam", "silt", "saline"]
    for s in soils:
        if s in msg:
            user.soil_type = s.capitalize()
            memory_engine.store_memory(db, user.user_id, f"Farmer field has {s.capitalize()} soil", category="soil")
            break

    # 3. Land size detection
    import re
    match = re.search(r"(\d+)\s*(acre|acres|kanal|kanals|maund|maunds)", msg)
    if match:
        size = match.group(1)
        unit = match.group(2)
        user.land_size_acres = f"{size} {unit}"
        memory_engine.store_memory(db, user.user_id, f"Farmer farm size is {size} {unit}", category="land")

    # 4. Crop detection
    crops = ["wheat", "rice", "cotton", "mustard", "tomatoes", "potato", "onion"]
    for c in crops:
        if c in msg:
            # Add a farm event for crop cultivation if not already added
            existing_event = db.query(FarmEvent).filter(
                FarmEvent.user_id == user.user_id,
                FarmEvent.crop_name == c.capitalize()
            ).first()
            if not existing_event:
                ev = FarmEvent(
                    user_id=user.user_id,
                    event_type="Cultivation",
                    crop_name=c.capitalize(),
                    crop_variety="Local standard",
                    details=f"Farmer mentioned cultivating {c.capitalize()} in conversation."
                )
                db.add(ev)
            memory_engine.store_memory(db, user.user_id, f"Farmer is growing {c.capitalize()}", category="crop")
            break

    db.commit()


@router.post("/message", response_model=ChatMessageResponse)
async def chat_message(
    payload: ChatMessageRequest,
    db: Session = Depends(get_db),
    opt_user: User | None = Depends(get_optional_user)
):
    # Resolve user
    user_id = payload.user_id
    if not user_id:
        if opt_user:
            user_id = opt_user.user_id
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token or user_id required"
            )

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        # Auto-create user if user_id was supplied but doesn't exist
        user = User(user_id=user_id, full_name="Guest Farmer", is_guest=True)
        db.add(user)
        db.commit()
        db.refresh(user)

    # Detect language
    lang = payload.language or detect_language(payload.message)

    # Extract memories from the incoming message & update SQLite User profile
    _extract_and_update_profile(db, user, payload.message)

    # Load history
    history_records = db.query(Conversation).filter(
        Conversation.user_id == user_id,
        Conversation.session_id == (payload.session_id or "default_session")
    ).order_by(Conversation.timestamp.asc()).limit(10).all()

    history = [{"role": r.role, "content": r.content} for r in history_records]

    # Gather Agent Context (Multi-Agent System)
    agent_ctx, agents_used = await orchestrator.gather_context(db, user_id, payload.message)

    # Recall Memories
    memory_recall = memory_engine.recall_memories(db, user_id, payload.message, limit=3)
    profile_ctx = memory_engine.get_profile_context(db, user_id)

    # Synthesize context
    system_context = (
        f"{profile_ctx}\n"
        f"--- ACTIVE AGENT ADVISORIES ---\n"
        f"{agent_ctx}\n"
    )

    # Call Qwen
    response_text, brain_mode = await qwen_client.generate_response(
        message=payload.message,
        system_context=system_context,
        history=history
    )

    # Save to conversations
    user_msg = Conversation(
        user_id=user_id,
        session_id=payload.session_id or "default_session",
        role="user",
        content=payload.message,
        language=lang
    )
    bot_msg = Conversation(
        user_id=user_id,
        session_id=payload.session_id or "default_session",
        role="assistant",
        content=response_text,
        language=lang
    )
    db.add(user_msg)
    db.add(bot_msg)
    db.commit()

    # Save new insights to persistent Memory if Qwen extracted something important
    if "wheat" in response_text.lower():
        memory_engine.store_memory(db, user_id, "Farmer received advice regarding wheat cultivation.", "crop_guide")

    return ChatMessageResponse(
        response=response_text,
        language=lang,
        session_id=payload.session_id or "default_session",
        agents_used=agents_used,
        memory_recall=memory_recall,
        confidence=0.92 if brain_mode == "qwen" else 0.75
    )
