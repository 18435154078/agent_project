from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # 跨域
import uvicorn
from contextlib import asynccontextmanager
from core.exception import global_exception_handler
from core.config import settings
from core.logger import logger
from api.health import router as health_router
from api.chat import router as chat_router
from api.rag import router as rag_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时
    logger.info("服务启动成功")
    yield
    # 关闭时
    logger.info("服务关闭")

app = FastAPI(title="AI智能助手", version="1.0", lifespan=lifespan)

app.add_exception_handler(Exception, global_exception_handler)

# 跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 加载路由
app.include_router(health_router)
app.include_router(chat_router)
app.include_router(rag_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.SERVER_HOST, port=settings.SERVER_PORT, reload=True)