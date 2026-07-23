from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.config import settings
from app.core.logging import logger
from app.engine.database import init_engine, get_sessionmaker


# Initialize the database engine
init_engine()

# Get session maker
async_session = get_sessionmaker()


class Base(DeclarativeBase):
    pass


async def init_db() -> None:
    logger.info("Initializing database...")
    from sqlalchemy.ext.asyncio import create_async_engine
    engine = create_async_engine(settings.database_url, echo=False)
    async with engine.begin() as conn:
        # Use our own Base class for creating tables
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized successfully")


async def get_session():
    async with async_session() as session:
        yield session