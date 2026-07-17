"""
Database engine initialization and configuration.
"""
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings
from app.core.logging import logger

# Create the database engine
engine: AsyncEngine = None
sessionmaker = None

def init_engine() -> None:
    """Initialize the database engine."""
    global engine, sessionmaker
    
    if engine is None:
        from sqlalchemy.ext.asyncio import create_async_engine
        engine = create_async_engine(settings.database_url, echo=False)
        sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
        logger.info("Database engine initialized successfully")

def get_engine() -> AsyncEngine:
    """Get the database engine."""
    if engine is None:
        init_engine()
    return engine

def get_sessionmaker():
    """Get the session maker."""
    if sessionmaker is None:
        init_engine()
    return sessionmaker