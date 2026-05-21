from fastapi import APIRouter
from fastapi.responses import JSONResponse
import os

router = APIRouter()

@router.get("/health")
def health():
    ENV = os.getenv("ENV", "dev")
    print(ENV)
    return JSONResponse({"status": "ok", "service": "ai_assistant"})