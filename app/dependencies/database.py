from typing import AsyncGenerator

from fastapi import Depends
from fastapi_async_sqlalchemy import db
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency untuk mendapatkan database session."""
    async with db.session() as session:
        yield session


async def get_db() -> AsyncSession:
    """Dependency untuk mendapatkan database session (non-generator version)."""
    return db.session


# Type alias untuk model yang bisa digunakan di repositories
ModelType = Base
