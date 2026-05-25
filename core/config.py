from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
import sys

# 获取环境
ENV = os.getenv("ENV", "dev")
print(ENV)

load_dotenv(".env")
load_dotenv(f".env.{ENV}")

class Settings(BaseSettings):
    # # 服务
    SERVER_HOST: str
    SERVER_PORT: int


    # 大模型
    DOUBAO_API_KEY: str
    DOUBAO_BASE_URL: str
    DOUBAO_MODEL: str

    DEEPSEEK_API_KEY: str
    DEEPSEEK_BASE_URL: str
    DEEPSEEK_MODEL: str

    QWEN_API_KEY: str
    QWEN_BASE_URL: str
    QWEN_EMBEDDING_MODEL: str


    # Redis
    REDIS_HOST: str
    REDIS_PORT: int 
    REDIS_DB: int = 0

    # RAG
    CHROMA_DB_DIR: str = "./chroma_db"
    UPLOAD_DIR: str = "./uploads"

    # class Config:
    #     env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")

settings = Settings()