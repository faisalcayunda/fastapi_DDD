from functools import lru_cache

from .app import AppSettings
from .database import DatabaseSettings
from .security import SecuritySettings
from .storage import StorageSettings


@lru_cache
def get_app_settings() -> AppSettings:
    """Get cached app settings."""
    return AppSettings()


@lru_cache
def get_database_settings() -> DatabaseSettings:
    """Get cached database settings."""
    return DatabaseSettings()


@lru_cache
def get_security_settings() -> SecuritySettings:
    """Get cached security settings."""
    return SecuritySettings()


@lru_cache
def get_storage_settings() -> StorageSettings:
    """Get cached storage settings."""
    return StorageSettings()


# Initialize settings
app_settings = get_app_settings()
db_settings = get_database_settings()
security_settings = get_security_settings()
storage_settings = get_storage_settings()
