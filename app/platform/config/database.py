from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database settings."""

    # Database URL
    DATABASE_URL: str

    # Connection Pool Settings
    POOL_SIZE: int = Field(default=5)
    MAX_OVERFLOW: int = Field(default=10)
    POOL_TIMEOUT: int = Field(default=30)
    POOL_RECYCLE: int = Field(default=3600)
    ECHO_SQL: bool = Field(default=False)

    # Settings config
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)
