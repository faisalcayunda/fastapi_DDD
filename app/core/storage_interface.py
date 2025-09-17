from abc import ABC, abstractmethod
from typing import BinaryIO, Optional, Tuple


class IStorage(ABC):
    """Storage interface for different storage implementations."""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize storage."""
        pass

    @abstractmethod
    async def upload_file(self, file: BinaryIO, object_name: str, content_type: Optional[str] = None) -> str:
        """Upload file to storage."""
        pass

    @abstractmethod
    async def download_file(self, object_name: str) -> Tuple[BinaryIO, str]:
        """Download file from storage."""
        pass

    @abstractmethod
    async def delete_file(self, object_name: str) -> None:
        """Delete file from storage."""
        pass

    @abstractmethod
    async def get_file_url(self, object_name: str, expires: int = 3600) -> str:
        """Get presigned URL for file."""
        pass

    @abstractmethod
    def get_file_path(self, object_name: str) -> str:
        """Get full path for file."""
        pass
