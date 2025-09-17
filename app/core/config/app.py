from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.utils.system import get_optimal_workers


class AppSettings(BaseSettings):
    """Application settings."""

    # Application settings
    PROJECT_NAME: str = Field(default="SIPS")
    VERSION: str = Field(default="0.1.0")
    DESCRIPTION: str = Field(default="SIPS API")
    TIMEZONE: str = Field(default="Asia/Jakarta")

    # Server settings
    DEBUG: bool = Field(default=False)
    HOST: str = Field(default="127.0.0.1")
    PORT: int = Field(default=8000)
    WORKERS: int = Field(default=get_optimal_workers())
    LOG_LEVEL: str = Field(default="info")
    LOOP: str = Field(default="uvloop")
    HTTP: str = Field(default="httptools")

    # Performance settings
    LIMIT_CONCURRENCY: int = Field(default=100)
    BACKLOG: int = Field(default=2048)
    LIMIT_MAX_REQUESTS: int | None = Field(default=None)
    TIMEOUT_KEEP_ALIVE: int = Field(default=5)
    H11_MAX_INCOMPLETE_EVENT_SIZE: int = Field(default=16 * 1024)

    # Headers
    SERVER_HEADER: str = Field(default=None)
    FORWARDED_ALLOW_IPS: str = Field(default="*")
    DATE_HEADER: bool = Field(default=True)

    # CORS
    ALLOWED_ORIGINS: List[str] = Field(default=["*"])

    @property
    def ACCESS_LOG(self) -> bool:
        return self.DEBUG

    # Settings config
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="allow")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.SERVER_HEADER is None:
            self.SERVER_HEADER = f"{self.PROJECT_NAME}/{self.VERSION}"
