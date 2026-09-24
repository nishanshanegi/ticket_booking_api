# This file securely loads your database credentials from a .env file and validates them.
# app/core/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "High-Concurrency Ticket API"
    # Notice we use postgresql+asyncpg for async operations
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/ticket_db"
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"

settings = Settings()