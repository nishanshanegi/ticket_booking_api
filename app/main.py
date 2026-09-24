# app/main.py
from fastapi import FastAPI
from app.core.database import engine, Base
from app.core.config import settings
import logging
from app.api.v1 import bookings,events

# Ensure models are loaded
from app.models.domain import Event, Seat, Booking

# Setup structured logging (Roadmap Day 46)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="High-Concurrency Ticket Booking API",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database...")
    async with engine.begin() as conn:
        # NOTE: In production, we use Alembic for migrations (Day 13). 
        # We use create_all here for rapid prototyping.
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized!")

app.include_router(bookings.router, prefix="/api/v1/bookings", tags=["Bookings"])
app.include_router(events.router, prefix="/api/v1/events", tags=["Events"]) # <-- add this line

@app.get("/health")
async def health_check():
    return {"status": "ok"}