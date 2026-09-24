# app/api/v1/bookings.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.booking import ReserveSeatRequest, SeatResponse
from app.services.booking_service import reserve_seat_with_preferences

# ADD THIS IMPORT:
from app.core.redis import redis_client

router = APIRouter()

@router.post("/reserve", response_model=SeatResponse, status_code=200)
async def reserve_seat_endpoint(
    request: ReserveSeatRequest,
    db: AsyncSession = Depends(get_db) 
):
    seat = await reserve_seat_with_preferences(
        db=db,
        event_id=request.event_id,
        user_id=request.user_id,
        preferred_seat_id=request.preferred_seat_id,
        allow_any_seat=request.allow_any_seat
    )
    
    # SENIOR FLEX (CACHE INVALIDATION):
    # Now that a seat status changed, we destroy the old cache.
    # The next person to view the map will trigger a fresh Postgres query.
    await redis_client.delete(f"event:{request.event_id}:seats")
    
    return seat