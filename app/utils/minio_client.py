from typing import Any, BinaryIO, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from fastapi import HTTPException, status
from miniopy_async import Minio
from miniopy_async.error import S3Error

from app.core.config import settings


class MinioClient:
    """
    Client class untuk interaksi dengan MinIO Object Storage secara asinkron.
    """

    def __init__(self):
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT_URL,
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=settings.MINIO_SECURE,
            region=settings.MINIO_REGION,
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME

    async def init_bucket(self) -> None:
        """
        Inisialisasi bucket jika belum ada.
        """
        try:
            if not await self.client.bucket_exists(self.bucket_name):
                await self.client.make_bucket(self.bucket_name)
                # Set bucket policy agar dapat diakses publik jika diperlukan
                # policy = {...}  # Define your policy if needed
                # await self.client.set_bucket_policy(self.bucket_name, json.dumps(policy))
        except S3Error as err:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error initializing MinIO bucket: {str(err)}",
            )

    async def upload_file(
        self,
        file_data: BinaryIO,
        object_name: str,
        content_type: str,
        content_length: int,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Upload file ke MinIO.

        Args:
            file_data: File-like object untuk diupload
            object_name: Nama objek di MinIO
            content_type: Tipe konten file
            metadata: Metadata tambahan untuk objek

        Returns:
            URL objek yang telah diupload
        """
        try:
            await self.init_bucket()

            # Upload file
            await self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file_data,
                length=content_length,
                content_type=content_type,
                metadata=metadata,
            )

            # Generate URL
            url = await self.get_file_url(object_name)
            return url

        except S3Error as err:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error uploading file to MinIO: {str(err)}",
            )

    async def get_file(self, object_name: str) -> Tuple[BinaryIO, Dict[str, Any]]:
        """
        Ambil file dari MinIO.

        Args:
            object_name: Nama objek di MinIO

        Returns:
            Tuple dari (file data, object info)
        """
        try:
            stat = await self.client.stat_object(bucket_name=self.bucket_name, object_name=object_name)

            response = await self.client.get_object(bucket_name=self.bucket_name, object_name=object_name)

            return response, stat.__dict__

        except S3Error as err:
            if err.code == "NoSuchKey":
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving file from MinIO: {str(err)}",
            )

    async def delete_file(self, object_name: str) -> bool:
        """
        Hapus file dari MinIO.

        Args:
            object_name: Nama objek di MinIO

        Returns:
            Boolean yang menunjukkan keberhasilan operasi
        """
        try:
            await self.client.remove_object(self.bucket_name, object_name)
            return True
        except S3Error as err:
            if err.code == "NoSuchKey":
                return False
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting file from MinIO: {str(err)}",
            )

    async def get_file_url(self, object_name: str) -> str:
        """
        Dapatkan URL untuk mengakses file.

        Args:
            object_name: Nama objek di MinIO

        Returns:
            URL untuk mengakses file
        """
        try:
            # For public access
            if settings.MINIO_SECURE:
                protocol = "https"
            else:
                protocol = "http"

            parsed_endpoint = urlparse(settings.MINIO_ENDPOINT_URL)
            host = parsed_endpoint.netloc or settings.MINIO_ENDPOINT_URL

            return f"{protocol}://{host}/{self.bucket_name}/{object_name}"

            # For presigned URL (time-limited access):
            # return await self.client.presigned_get_object(
            #     bucket_name=self.bucket_name,
            #     object_name=object_name,
            #     expires=timedelta(hours=1)
            # )

        except S3Error as err:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating URL: {str(err)}",
            )

    async def list_files(self, prefix: str = "", recursive: bool = True) -> List[Dict[str, Any]]:
        """
        Daftar semua file di dalam bucket dengan prefix tertentu.

        Args:
            prefix: Awalan objek yang dicari
            recursive: Jika True, juga mencari di subdirektori

        Returns:
            List dari item objek
        """
        try:
            objects = []
            async for obj in self.client.list_objects(self.bucket_name, prefix=prefix, recursive=recursive):
                objects.append(
                    {
                        "name": obj.object_name,
                        "size": obj.size,
                        "last_modified": obj.last_modified,
                        "etag": obj.etag,
                    }
                )
            return objects
        except S3Error as err:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error listing files: {str(err)}",
            )
