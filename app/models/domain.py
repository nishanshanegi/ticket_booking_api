# app/models/domain.py

# We use Python enum to strictly enforce statuses (preventing bad data).
# Look at the __table_args__ in the Seat model. We are creating a Composite Index because we know our most frequent query will be checking if a specific event has available seats.


import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class SeatStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    LOCKED = "LOCKED"      # In someone's cart
    BOOKED = "BOOKED"      # Paid for

class BookingStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"

class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    total_seats = Column(Integer, nullable=False)

    seats = relationship("Seat", back_populates="event", cascade="all, delete")

class Seat(Base):
    __tablename__ = "seats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    seat_number = Column(String, nullable=False)
    status = Column(Enum(SeatStatus), default=SeatStatus.AVAILABLE, nullable=False)
    
    locked_by_user_id = Column(UUID(as_uuid=True), nullable=True)
    locked_until = Column(DateTime, nullable=True)

    event = relationship("Event", back_populates="seats")

    # SENIOR FLEX: Indexing the exact columns we use in our WHERE clause (Day 14)
    __table_args__ = (
        Index('idx_event_status', 'event_id', 'status'),
    )

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    seat_id = Column(UUID(as_uuid=True), ForeignKey("seats.id"), nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    
    # SENIOR FLEX: Idempotency Key to prevent double charges (Day 32)
    idempotency_key = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)