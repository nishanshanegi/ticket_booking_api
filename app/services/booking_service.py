# app/services/booking_service.py
import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from sqlalchemy.exc import OperationalError

from app.models.domain import Seat, SeatStatus

async def reserve_seat_with_preferences(
    db: AsyncSession, 
    event_id: uuid.UUID, 
    user_id: uuid.UUID, 
    preferred_seat_id: uuid.UUID, 
    allow_any_seat: bool
) -> Seat:
    """
    Attempts to reserve a preferred seat. If taken, falls back to any available seat
    based on the user's preference.
    """
    seat_to_reserve = None

    # --- STEP 1: Try to get the EXACT seat they want (using NOWAIT) ---
    try:
        specific_seat_query = (
            select(Seat)
            .where(
                Seat.id == preferred_seat_id,
                Seat.event_id == event_id,
                Seat.status == SeatStatus.AVAILABLE
            )
            .with_for_update(nowait=True) # Fail instantly if someone else is locking it
        )
        result = await db.execute(specific_seat_query)
        seat_to_reserve = result.scalars().first()
        
    except OperationalError:
        # We catch the lock error. Someone else is literally buying it right now.
        seat_to_reserve = None

    # --- STEP 2: Handle the failure based on User Preference ---
    if not seat_to_reserve:
        if not allow_any_seat:
            # The user ONLY wanted that exact seat. Tell them it's gone.
            raise HTTPException(
                status_code=409, 
                detail="Your preferred seat is no longer available. Please select another map seat."
            )
        else:
            # The user said "Just get me any seat!" Let's find one using SKIP LOCKED.
            fallback_query = (
                select(Seat)
                .where(
                    Seat.event_id == event_id,
                    Seat.status == SeatStatus.AVAILABLE
                )
                .limit(1)
                .with_for_update(skip_locked=True) # Skip whatever is locked, find a free one
            )
            fallback_result = await db.execute(fallback_query)
            seat_to_reserve = fallback_result.scalars().first()

            if not seat_to_reserve:
                # If this is still None, the whole event is sold out!
                raise HTTPException(
                    status_code=409, 
                    detail="Event is completely sold out!"
                )

    # --- STEP 3: Lock the seat (Whichever one we successfully got) ---
    seat_to_reserve.status = SeatStatus.LOCKED
    seat_to_reserve.locked_by_user_id = user_id
    seat_to_reserve.locked_until = datetime.utcnow() + timedelta(minutes=10)
    
    # Commit changes to the database
    await db.commit()
    await db.refresh(seat_to_reserve)
    
    return seat_to_reserve