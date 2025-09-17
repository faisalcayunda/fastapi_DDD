"""
Database Connection Test Script
Tests async database operations and connection handling
"""

import asyncio
import logging
import sys

from sqlalchemy import text

from app.utils.db_manager import cleanup_database_connections, db_manager, health_check

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_database_connection():
    """Test database connection and basic operations"""
    try:
        logger.info("Testing database connection...")

        # Test connection
        is_connected = await health_check()
        if not is_connected:
            logger.error("Database connection failed")
            return False

        logger.info("Database connection successful")

        # Test basic query
        async with db_manager.get_connection() as conn:
            result = await conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            if row and row[0] == 1:
                logger.info("Basic query test passed")
            else:
                logger.error("Basic query test failed")
                return False

        logger.info("All database tests passed")
        return True

    except Exception as e:
        logger.error(f"Database test failed: {e}")
        return False
    finally:
        await cleanup_database_connections()


async def main():
    """Main test function"""
    logger.info("Starting database connection tests...")

    success = await test_database_connection()

    if success:
        logger.info("All tests completed successfully")
        sys.exit(0)
    else:
        logger.error("Tests failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
