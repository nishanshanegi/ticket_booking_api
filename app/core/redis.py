# app/core/redis.py
import redis.asyncio as redis
from app.core.config import settings

# decode_responses=True means Redis will return Python strings instead of raw bytes
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)