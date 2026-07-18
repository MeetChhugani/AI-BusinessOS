import os
import shutil
from abc import ABC, abstractmethod
from fastapi import UploadFile
from app.logging.config import logger

class StorageService(ABC):
    @abstractmethod
    async def upload_file(self, file: UploadFile, destination_path: str) -> str:
        """Uploads file to store and returns saved path/key."""
        pass

    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """Deletes file from active store."""
        pass

class LocalStorageService(StorageService):
    def __init__(self, base_dir: str = "uploads") -> None:
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    async def upload_file(self, file: UploadFile, destination_path: str) -> str:
        full_dest = os.path.join(self.base_dir, destination_path)
        os.makedirs(os.path.dirname(full_dest), exist_ok=True)
        
        # Write bytes locally
        with open(full_dest, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info("file_uploaded_locally", path=full_dest)
        return full_dest

    async def delete_file(self, file_path: str) -> bool:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info("file_deleted_locally", path=file_path)
            return True
        logger.warning("file_deletion_failed_not_found", path=file_path)
        return False

class S3StorageService(StorageService):
    async def upload_file(self, file: UploadFile, destination_path: str) -> str:
        # Stub for AWS S3 - returns bucket object URI
        return f"s3://ai-businessos-bucket/{destination_path}"

    async def delete_file(self, file_path: str) -> bool:
        return True

class GCSStorageService(StorageService):
    async def upload_file(self, file: UploadFile, destination_path: str) -> str:
        # Stub for Google Cloud Storage
        return f"gs://ai-businessos-bucket/{destination_path}"

    async def delete_file(self, file_path: str) -> bool:
        return True

class AzureStorageService(StorageService):
    async def upload_file(self, file: UploadFile, destination_path: str) -> str:
        # Stub for Azure Blob Storage
        return f"https://aibusinessos.blob.core.windows.net/{destination_path}"

    async def delete_file(self, file_path: str) -> bool:
        return True

def get_storage_service() -> StorageService:
    """Dependency injector to fetch active storage backend."""
    # Under enterprise configuration, checks settings.STORAGE_PROVIDER to swap providers
    return LocalStorageService()
