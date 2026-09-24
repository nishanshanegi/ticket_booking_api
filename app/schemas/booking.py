# app/schemas/booking.py
# This automatically validates the JSON payload from the frontend. If a user sends a bad UUID or a string instead of a boolean, FastAPI blocks it before it hits your database.
# The Pydantic Schemas (Data Validation)
from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from typing import Optional

class ReserveSeatRequest(BaseModel):
    event_id: uuid.UUID
    preferred_seat_id: uuid.UUID
    # We require a user_id here just to simulate a logged-in user for now
    user_id: uuid.UUID 
    allow_any_seat: bool = Field(
        default=False, 
        description="If True, will find any available seat if preferred is taken."
    )

class SeatResponse(BaseModel):
    id: uuid.UUID
    seat_number: str
    status: str
    locked_until: Optional[datetime]

    # SENIOR FLEX: This tells Pydantic to read data directly from the SQLAlchemy ORM model
    class Config:
        from_attributes = True