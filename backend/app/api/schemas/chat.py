from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    image_data_url: str | None = None


class Citation(BaseModel):
    title: str
    source: str | None = None
    snippet: str


class ChatResponse(BaseModel):
    answer: str
    farmer_id: int
    memory_used: dict
    citations: list[Citation] = []
    mode: str
