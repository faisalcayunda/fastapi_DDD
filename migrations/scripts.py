import asyncio
import os
import shutil
import sys

from dotenv import load_dotenv

# Add the app directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.utils.db_manager import full_migration_process

load_dotenv()


async def main():
    """Main async function with proper error handling"""
    version_folder = "migrations/versions"

    # Create versions directory if it doesn't exist
    if not os.path.exists(version_folder):
        os.makedirs(version_folder)

    try:
        print("Starting migration process...")
        success = await full_migration_process()

        if not success:
            print("Migration failed")
            sys.exit(1)
        else:
            print("Migration completed successfully")

    except Exception as e:
        print(f"Error during migration: {e}")
        sys.exit(1)
    finally:
        # Clean up version folder
        if os.path.exists(version_folder):
            shutil.rmtree(version_folder)


if __name__ == "__main__":
    asyncio.run(main())
