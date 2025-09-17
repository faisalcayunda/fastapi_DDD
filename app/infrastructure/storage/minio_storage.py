from typing import BinaryIO, Optional, Tuple

from minio import Minio
from minio.error import MinioException

from app.core.config import settings
from app.core.exceptions import StorageException
from app.domain.interfaces.storage_interface import IStorage


class MinioStorage(IStorage):
    """MinIO storage implementation."""

    def __init__(self):
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT_URL.replace("http://", "").replace("https://", ""),
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=settings.MINIO_SECURE,
            region=settings.MINIO_REGION,
        )
        self.bucket = settings.MINIO_BUCKET_NAME

    async def initialize(self) -> None:
        """Initialize storage."""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
        except MinioException as e:
            raise StorageException(f"Failed to initialize storage: {str(e)}")

    async def upload_file(self, file: BinaryIO, object_name: str, content_type: Optional[str] = None) -> str:
        """Upload file to storage."""
        try:
            # Get file size
            file.seek(0, 2)  # Seek to end
            size = file.tell()
            file.seek(0)  # Seek back to start

            # Check file size
            if size > settings.MAX_UPLOAD_SIZE:
                raise StorageException(f"File size exceeds limit of {settings.MAX_UPLOAD_SIZE} bytes")

            # Upload file
            self.client.put_object(
                bucket_name=self.bucket,
                object_name=object_name,
                data=file,
                length=size,
                content_type=content_type,
            )

            return object_name
        except MinioException as e:
            raise StorageException(f"Failed to upload file: {str(e)}")

    async def download_file(self, object_name: str) -> Tuple[BinaryIO, str]:
        """Download file from storage."""
        try:
            # Get object
            obj = self.client.get_object(bucket_name=self.bucket, object_name=object_name)
            return obj, obj.headers.get("content-type", "application/octet-stream")
        except MinioException as e:
            raise StorageException(f"Failed to download file: {str(e)}")

    async def delete_file(self, object_name: str) -> None:
        """Delete file from storage."""
        try:
            self.client.remove_object(bucket_name=self.bucket, object_name=object_name)
        except MinioException as e:
            raise StorageException(f"Failed to delete file: {str(e)}")

    async def get_file_url(self, object_name: str, expires: int = 3600) -> str:
        """Get presigned URL for file."""
        try:
            return self.client.presigned_get_object(bucket_name=self.bucket, object_name=object_name, expires=expires)
        except MinioException as e:
            raise StorageException(f"Failed to get file URL: {str(e)}")

    def get_file_path(self, object_name: str) -> str:
        """Get full path for file."""
        return f"{settings.MINIO_ENDPOINT_URL}/{self.bucket}/{object_name}"
