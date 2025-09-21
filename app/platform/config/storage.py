from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class StorageSettings(BaseSettings):
    """Storage settings for S3/MinIO."""

    # MinIO Settings
    MINIO_ENDPOINT_URL: str = Field(default="http://localhost:9000")
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_SECURE: Optional[bool] = False
    MINIO_BUCKET_NAME: Optional[str] = Field(default="sips")
    MINIO_REGION: Optional[str] = Field(default=None)

    # Upload Settings
    MAX_UPLOAD_SIZE: int = Field(default=100 * 1024 * 1024)  # 100MB default limit
    ALLOWED_EXTENSIONS: List[str] = [
        "jpg",
        "jpeg",
        "png",
        "pdf",
        "doc",
        "docx",
        "xls",
        "xlsx",
        "txt",
        "csv",
        "zip",
        "rar",
        "json",
    ]

    # Cache Settings
    CACHE_CONTROL: str = Field(default="max-age=3600")
    CACHE_EXPIRES: int = Field(default=3600)  # 1 hour

    # Settings config
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)
