from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas.chat import ChatRequest, ChatResponse
from app.core.memory_agent import MemoryAgent
from app.db.models import ChatMessage
from app.db.session import get_db

router = APIRouter(prefix="/chat", tags=["chat"])
agent = MemoryAgent()


@router.post("/message", response_model=ChatResponse)
async def send_message(payload: ChatRequest, db: Session = Depends(get_db)):
    return await agent.answer(db, payload.farmer_id, payload.message)


@router.get("/history")
def get_history(farmer_id: int = 1, db: Session = Depends(get_db)):
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.farmer_id == farmer_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    return [
        {
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at.isoformat() if msg.created_at else None
        }
        for msg in messages
    ]
