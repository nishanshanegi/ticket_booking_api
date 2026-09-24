# This creates the async connection pool and our Dependency Injection function (get_db) that we will use in our routers.
# app/core/database.py

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# echo=True prints SQL queries to terminal (great for debugging N+1 issues)
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# The session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

Base = declarative_base()

# Dependency Injection for FastAPI (Roadmap Day 5)
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()