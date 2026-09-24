# app/tasks/seat_tasks.py
import asyncio
import uuid
from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from sqlalchemy import select
from app.models.domain import Seat, SeatStatus
from app.core.redis import redis_client

async def _release_seat_async(seat_id: str, event_id: str):
    """The actual database logic to release the seat"""
    async with AsyncSessionLocal() as db:
        query = select(Seat).where(Seat.id == uuid.UUID(seat_id))
        result = await db.execute(query)
        seat = result.scalars().first()

        # If it's STILL locked after the timer finishes, release it!
        if seat and seat.status == SeatStatus.LOCKED:
            seat.status = SeatStatus.AVAILABLE
            seat.locked_by_user_id = None
            seat.locked_until = None
            await db.commit()
            
            # SENIOR FLEX: We must delete the cache again so the public sees it's available!
            await redis_client.delete(f"event:{event_id}:seats")
            print(f"🚨 CART ABANDONED! Seat {seat.seat_number} released back to public.")

@celery_app.task(name="release_unpaid_seat")
def release_unpaid_seat(seat_id: str, event_id: str):
    """
    This is the function Celery will run in the background.
    Because Celery is synchronous, we use asyncio.run to execute our async DB code.
    """
    asyncio.run(_release_seat_async(seat_id, event_id))