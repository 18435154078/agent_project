from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from fastapi import HTTPException
from rag.knowledge_base_service import knowledge_base_service
from pydantic import Field, field_validator
from schemas.response import ApiResponse

router = APIRouter(prefix="/api/chat", tags=["对话接口"])

class ChatRequest(BaseModel):
    message: str = Field(..., description="用户输入的消息")
    session_id: Optional[str] = Field(None, description="会话ID，用于区分不同用户的对话历史")
    @field_validator("message")
    def check_message_not_empty(cls, v):
        if not v or not v.strip():
            raise HTTPException(status_code=400, detail="message不能为空")
        return v.strip()

    @field_validator("session_id")
    def check_session_id_not_empty(cls, v):
        if not v or not v.strip():
            raise HTTPException(status_code=400, detail="session_id不能为空")
        return v.strip()

@router.post("/chat")
async def chat(req: ChatRequest):
    message = req.message
    session_id = req.session_id
    response = knowledge_base_service.chat(message, session_id)
    return ApiResponse(data=response)


@router.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    message = req.message
    session_id = req.session_id
    return knowledge_base_service.chat_stream(message, session_id)
    