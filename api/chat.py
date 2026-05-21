from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json

from core.config import settings
from core.logger import logger
from memory.redis_conn import save_message, get_history
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

router = APIRouter(prefix="/api/chat", tags=["对话接口"])

# 初始化大模型
llm = ChatOpenAI(
    openai_api_key=settings.DOUBAO_API_KEY,
    openai_api_base=settings.DOUBAO_BASE_URL,
    model=settings.DOUBAO_MODEL,
    streaming=True,
    temperature=0
)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

@router.post("/stream")
async def chat_stream(req: ChatRequest):
    session_id = req.session_id or f"session_{id(req)}"

    # 1. 保存用户消息到Redis
    save_message(session_id, "user", req.message)
    history = get_history(session_id)

    # 2. 拼接历史对话为消息列表
    messages = [SystemMessage(content="你是一个脾气暴躁的AI助手，简要回答。")]
    for line in reversed(history):
        role, content = line.split(":", 1)
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append({"role": "assistant", "content": content})

    logger.info(f"收到请求，session_id: {session_id}")

    # 3. 流式返回
    async def generate():
        response_content = ""
        async for chunk in llm.astream(messages):
            if chunk.content:
                response_content += chunk.content
                yield f"data: {json.dumps({'content': chunk.content}, ensure_ascii=False)}\n\n"
        # 保存AI回复到Redis
        save_message(session_id, "assistant", response_content)
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")