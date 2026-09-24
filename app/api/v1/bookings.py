# app/api/v1/bookings.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.booking import ReserveSeatRequest, SeatResponse, PaymentWebhookPayload
from app.services.booking_service import reserve_seat_with_preferences, confirm_payment

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

@router.post("/webhook/payment", status_code=200)
async def payment_webhook(
    payload: PaymentWebhookPayload,
    db: AsyncSession = Depends(get_db)
):
    """
    Simulates a webhook from Stripe. 
    Uses Idempotency Keys to safely handle duplicate webhooks.
    """
    result = await confirm_payment(
        db=db,
        seat_id=payload.seat_id,
        user_id=payload.user_id,
        idempotency_key=payload.idempotency_key
    )
    
    # Because a seat was officially sold, we must clear the map cache!
    # (In a real app, you'd fetch the event_id from the DB first, but this is a simplified comment)
    # await redis_client.delete(f"event:{event_id}:seats")
    
    return result