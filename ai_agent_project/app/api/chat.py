from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import LLMClient


@router.post("/chat")
async def chat(request: ChatRequest):

    answer = await llm_service.chat(request.message)

    return ChatResponse(answer=answer)
