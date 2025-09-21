from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.platform.config import app_settings, db_settings

# Create async engine
engine = create_async_engine(
    db_settings.DATABASE_URL,
    echo=app_settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=db_settings.POOL_RECYCLE,
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        return session


# Dependency
def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    return get_session()
