# We need a background worker. When a seat is locked, we will tell our background worker (Celery):
# "Hey, set a timer for 10 minutes. When the timer goes off, check if this seat is still 'LOCKED' (meaning they never paid). If it is, change it back to 'AVAILABLE' and delete the Redis cache!"

# This configures Celery to use your running Redis container as its "message broker" (where it stores the pending timers).

# app/core/celery_app.py
from celery import Celery
from app.core.config import settings

# Initialize Celery and explicitly INCLUDE our tasks file
celery_app = Celery(
    "ticket_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['app.tasks.seat_tasks']  # <-- This fixes the KeyError!
)