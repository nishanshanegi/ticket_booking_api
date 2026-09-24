# app/api/v1/events.py
import json
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.redis import redis_client
from app.models.domain import Seat
from app.schemas.booking import SeatResponse

router = APIRouter()

@router.get("/{event_id}/seats", response_model=list[SeatResponse])
async def get_event_seats(event_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Get all seats for an event. 
    Uses Redis caching to prevent database meltdowns during traffic spikes.
    """
    cache_key = f"event:{event_id}:seats"
    
    # 1. Check Redis Cache First
    cached_seats = await redis_client.get(cache_key)
    if cached_seats:
        print("⚡ SPEED BOOST: Serving from Redis Cache!")
        return json.loads(cached_seats)
        
    print("🐢 CACHE MISS: Querying PostgreSQL...")
    
    # 2. If not in cache, query Postgres
    query = select(Seat).where(Seat.event_id == event_id)
    result = await db.execute(query)
    seats = result.scalars().all()
    
    # 3. Serialize data and save to Redis for 60 seconds
    # (We use Pydantic to easily convert UUIDs and Datetimes to JSON strings)
    seats_data = [
        SeatResponse.model_validate(seat).model_dump(mode='json') 
        for seat in seats
    ]
    await redis_client.set(cache_key, json.dumps(seats_data), ex=60)
    
    return seats