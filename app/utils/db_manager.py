"""
Database Management Utilities
Provides robust async database operations with proper connection handling
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections with proper async handling"""

    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or settings.DATABASE_URL
        self._engine: Optional[AsyncEngine] = None

    @property
    def engine(self) -> AsyncEngine:
        """Get or create the async engine with proper configuration"""
        if self._engine is None:
            self._engine = create_async_engine(
                self.database_url,
                poolclass=NullPool,  # Use NullPool for migrations
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False,
                future=True,
            )
        return self._engine

    async def dispose(self):
        """Properly dispose the engine"""
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None

    @asynccontextmanager
    async def get_connection(self):
        """Get a database connection with proper cleanup"""
        async with self.engine.connect() as connection:
            yield connection

    @asynccontextmanager
    async def get_transaction(self):
        """Get a database transaction with proper cleanup"""
        async with self.engine.begin() as transaction:
            yield transaction

    async def execute_query(self, query: str, params: Optional[dict] = None):
        """Execute a raw SQL query"""
        async with self.get_connection() as conn:
            result = await conn.execute(text(query), params or {})
            return result

    async def drop_table_if_exists(self, table_name: str):
        """Drop a table if it exists"""
        query = f"DROP TABLE IF EXISTS {table_name} CASCADE"
        await self.execute_query(query)
        logger.info(f"Dropped table: {table_name}")

    async def check_connection(self) -> bool:
        """Check if database connection is working"""
        try:
            async with self.get_connection() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager()


async def cleanup_database_connections():
    """Cleanup function for database connections"""
    await db_manager.dispose()


async def health_check():
    """Database health check"""
    return await db_manager.check_connection()


# Migration utilities
async def reset_migrations():
    """Reset migration state by dropping alembic_version table"""
    try:
        await db_manager.drop_table_if_exists("alembic_version")
        logger.info("Migration state reset successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to reset migrations: {e}")
        return False


async def run_migration_commands():
    """Run migration commands with proper error handling"""
    import subprocess

    commands = [
        ["alembic", "revision", "--autogenerate", "-m", "auto generated migration"],
        ["alembic", "upgrade", "head"],
    ]

    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Command {' '.join(cmd)} completed successfully")
            logger.debug(f"Output: {result.stdout}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Command {' '.join(cmd)} failed: {e}")
            logger.error(f"Error output: {e.stderr}")
            return False

    return True


async def full_migration_process():
    """Complete migration process with proper cleanup"""
    try:
        # Reset migration state
        if not await reset_migrations():
            return False

        # Run migrations
        if not await run_migration_commands():
            return False

        logger.info("Migration process completed successfully")
        return True

    except Exception as e:
        logger.error(f"Migration process failed: {e}")
        return False
    finally:
        # Always cleanup connections
        await cleanup_database_connections()


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Run full migration process
    success = asyncio.run(full_migration_process())
    sys.exit(0 if success else 1)
