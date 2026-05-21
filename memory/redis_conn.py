import redis
from core.config import settings

redis_client = redis.Redis(
    # db=settings.REDIS_DB,
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)

def save_message(session_id: str, role: str, content: str):
    redis_client.lpush(f"chat:{session_id}", f"{role}:{content}")
    redis_client.ltrim(f"chat:{session_id}", 0, 19)  # 保留最近20条

def get_history(session_id: str):
    return redis_client.lrange(f"chat:{session_id}", 0, -1)