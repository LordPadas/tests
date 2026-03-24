from fastapi import APIRouter
from pydantic import BaseModel

# Local, MVP: import from services Rag module
from ...services.rag import get_answer

router = APIRouter()


class ChatRequest(BaseModel):
    user_id: str
    room_id: str
    message: str


class Source(BaseModel):
    path: str
    name: str
    section: str | None = None
    confidence: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source] = []
    confidence: float = 0.0


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    answer, sources = get_answer(req.message)
    return ChatResponse(
        answer=answer,
        sources=[Source(**s) for s in sources],
        confidence=0.9,
    )
