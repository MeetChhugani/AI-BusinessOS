from typing import List
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user
from app.database.session import get_db_session
from app.models.storage import FileMetadata
from app.services.platform_service import FileStorageService
from app.schemas.platform import FileMetadataResponse

router = APIRouter(prefix="/files", tags=["File Storage Manager"])

@router.get("", response_model=List[FileMetadataResponse], summary="List uploaded metadata files")
async def list_files(
    db: AsyncSession = Depends(get_db_session)
) -> List[FileMetadata]:
    query = select(FileMetadata).where(FileMetadata.deleted_at.is_(None))
    res = await db.execute(query)
    return list(res.scalars().all())

@router.post("/upload", response_model=FileMetadataResponse, status_code=201, summary="Upload attachment file")
async def upload_file(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> FileMetadata:
    content = await file.read()
    meta = await FileStorageService.upload_file(
        db,
        name=file.filename or "unnamed_file",
        content=content,
        mime_type=file.content_type or "application/octet-stream",
        uploaded_by_id=current_user.id
    )
    return meta
