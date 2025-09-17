import io
import os
from datetime import datetime
from typing import Any, BinaryIO, Dict, List, Tuple

from fastapi import HTTPException, UploadFile, status
from pytz import timezone

from app.core.config import settings
from app.core.minio_client import MinioClient
from app.models.file_model import FileModel
from app.repositories.file_repository import FileRepository

from . import BaseService


class FileService(BaseService[FileModel, FileRepository]):
    def __init__(self, repository: FileRepository, minio_client: MinioClient):
        super().__init__(FileModel, repository)

        self.minio_client = minio_client

    async def validate_file_extension(self, filename: str) -> bool:
        """Validasi ekstensi file."""
        ext = os.path.splitext(filename)[1][1:].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            allowed_exts = ", ".join(settings.ALLOWED_EXTENSIONS)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ekstensi file tidak diperbolehkan. Ekstensi yang diperbolehkan: {allowed_exts}",
            )
        return True

    async def validate_file_size(self, file_size: int) -> bool:
        """Cek ukuran file."""
        if file_size > settings.MAX_UPLOAD_SIZE:
            max_size_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File terlalu besar. Ukuran maksimum adalah {max_size_mb:.1f}MB",
            )
        return True

    async def find_by_object_name(self, object_name: str) -> FileModel:
        return await self.repository.find_by_object_name(object_name)

    async def upload_file(self, file: UploadFile, description: str = None, user_id: str = None) -> FileModel:
        """
        Upload file ke MinIO dan simpan metadata ke database.

        Args:
            file: File yang diupload
            description: Deskripsi file (opsional)
            user_id: ID pengguna yang mengupload

        Returns:
            Model file yang telah disimpan
        """
        try:
            await self.validate_file_extension(file.filename)

            object_name = f"{datetime.now(timezone(settings.TIMEZONE)).strftime('%Y%m%d%S')}-{file.filename}"

            content = await file.read()
            content_length = len(content)

            await self.validate_file_size(content_length)

            file_data = io.BytesIO(content)

            metadata = {
                "filename": file.filename,
                "description": description or "",
                "uploaded_by": str(user_id),
            }

            url = await self.minio_client.upload_file(
                file_data=file_data,
                object_name=object_name,
                content_type=file.content_type,
                content_length=content_length,
                metadata=metadata,
            )

            file_data = {
                "filename": file.filename,
                "object_name": object_name,
                "content_type": file.content_type,
                "size": content_length,
                "description": description,
                "url": url,
                "user_id": user_id,
            }

            db_file = await self.create(file_data)
            return db_file

        except HTTPException as e:
            raise e
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal mengupload file",
            )

    async def get_file_content(
        self, file_id: int = None, object_name: str = None, db_check: bool = False
    ) -> Tuple[BinaryIO, Dict[str, Any], FileModel]:
        """
        Ambil konten file dari MinIO.

        Args:
            file_id: ID file di database
            object_name: Nama file di MinIO

        Returns:
            Tuple dari (file content, object info, file model)
        """
        try:
            if db_check:
                if file_id:
                    file_model = await self.find_by_id(file_id)
                elif object_name:
                    file_model = await self.find_by_object_name(object_name)
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="File ID atau Object Name harus diisi",
                    )

                if not file_model:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="File tidak ditemukan",
                    )

                object_name = file_model.object_name

            object_content, object_info = await self.minio_client.get_file(object_name=object_name)

            return object_content, object_info

        except HTTPException as e:
            raise e

    async def delete_file_with_content(self, file_id: str, user_id: str) -> bool:
        """
        Hapus file dari MinIO dan database.

        Args:
            file_id: ID file di database
            user_id: ID pengguna yang ingin menghapus file

        Returns:
            Boolean yang menunjukkan keberhasilan operasi
        """
        try:
            file_model = await self.find_by_id(file_id)
            if not file_model:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File tidak ditemukan")

            if str(file_model.uploaded_by) != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Anda tidak memiliki akses untuk menghapus file ini",
                )

            await self.minio_client.delete_file(file_model.object_name)

            await self.delete(file_id)

            return True

        except HTTPException as e:
            raise e
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal menghapus file",
            )

    async def get_files_by_user(self, user_id: str, limit: int = 100, offset: int = 0) -> Tuple[List[FileModel], int]:
        """
        Ambil daftar file yang diupload oleh user tertentu.

        Args:
            user_id: ID pengguna
            limit: Jumlah maksimum hasil yang dikembalikan
            offset: Offset untuk paginasi

        Returns:
            Tuple dari (list file, total_count)
        """
        filter_params = {"uploaded_by": user_id}
        return await self.find_all(filter=filter_params, limit=limit, offset=offset)
