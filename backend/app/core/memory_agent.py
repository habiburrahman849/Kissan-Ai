from sqlalchemy.orm import Session

from app.db.models import ChatMessage
from app.llm.qwen_client import QwenClient
from app.memory.mem0_client import Mem0Client
from app.memory.memory_extractor import extract_memory_facts
from app.rag.retriever import AgricultureRetriever


class MemoryAgent:
    def __init__(self) -> None:
        self.memory = Mem0Client()
        self.retriever = AgricultureRetriever()
        self.llm = QwenClient()

    async def answer(self, db: Session, farmer_id: int, message: str, image_data_url: str | None = None) -> dict:
        self.memory.ensure_farmer(db, farmer_id)
        facts = await extract_memory_facts(message)
        self.memory.apply_facts(db, farmer_id, facts, message)
        memory = self.memory.get_profile(db, farmer_id)
        memory["mem0_memories"] = await self.memory.search_cloud_memories(farmer_id, message)
        retrieved = self.retriever.search(db, message, memory)
        science = [doc.__dict__ for doc in retrieved]

        # Retrieve last 10 messages of conversation history
        history_msgs = (
            db.query(ChatMessage)
            .filter(ChatMessage.farmer_id == farmer_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(10)
            .all()
        )
        history = [{"role": msg.role, "content": msg.content} for msg in reversed(history_msgs)]

        saved_user_msg = message
        if image_data_url:
            saved_user_msg = f"{message} [Uploaded crop photo]"

        db.add(ChatMessage(farmer_id=farmer_id, role="user", content=saved_user_msg))
        answer, mode = await self.llm.generate_urdu_answer(message, memory, science, history, image_data_url)
        db.add(ChatMessage(farmer_id=farmer_id, role="assistant", content=answer))
        db.commit()
        await self.memory.add_cloud_conversation(farmer_id, message, answer)

        return {
            "answer": answer,
            "farmer_id": farmer_id,
            "memory_used": memory,
            "citations": science,
            "mode": mode,
        }
