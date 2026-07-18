import os
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user
from app.database.session import get_db_session
from app.exceptions.custom_exceptions import EntityNotFoundException, PermissionDeniedException, ValidationException
from app.logging.config import logger
from app.models.hcm import Employee, EmployeeDocument
from app.models.user import User
from app.repositories.hcm_repository import EmployeeRepository
from app.schemas.hcm import EmployeeDocumentResponse
from app.services.storage_service import get_storage_service

router = APIRouter(prefix="/documents", tags=["Documents"])

# Enterprise size cap (10MB) and allowed extensions
MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/jpg",
    "text/csv",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", # xlsx
}

@router.post("/{employee_id}", response_model=EmployeeDocumentResponse, status_code=201, summary="Upload an employee document")
async def upload_document(
    employee_id: UUID,
    document_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> EmployeeDocument:
    emp_repo = EmployeeRepository(db)
    employee = await emp_repo.get_by_id(employee_id)
    if not employee:
        raise EntityNotFoundException("Employee profile not found")

    # Access security check
    if current_user.role not in ("SUPER_ADMIN", "ADMIN", "HR"):
        if employee.user_id != current_user.id:
            raise PermissionDeniedException("You do not have access to upload documents for this employee")

    # Validate size
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > MAX_FILE_SIZE:
        raise ValidationException("File size exceeds maximum threshold of 10MB")

    # Validate MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise ValidationException(f"Unsupported file format '{file.content_type}'. Supported: PDF, PNG, JPG, CSV, XLSX.")

    # Upload using StorageService abstraction
    storage = get_storage_service()
    dest_path = f"employee_{employee_id}/{document_type.lower().replace(' ', '_')}_{file.filename}"
    saved_path = await storage.upload_file(file, dest_path)

    doc = EmployeeDocument(
        employee_id=employee_id,
        name=file.filename or "Unnamed Document",
        document_type=document_type,
        file_path=saved_path,
        file_size=size,
        mime_type=file.content_type,
        version=1
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    
    logger.info("document_uploaded", doc_id=str(doc.id), mime=file.content_type)
    return doc

@router.get("/employee/{employee_id}", response_model=List[EmployeeDocumentResponse], summary="List employee documents")
async def list_employee_documents(
    employee_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> List[EmployeeDocument]:
    emp_repo = EmployeeRepository(db)
    employee = await emp_repo.get_by_id(employee_id)
    if not employee:
        raise EntityNotFoundException("Employee profile not found")
        
    if current_user.role not in ("SUPER_ADMIN", "ADMIN", "HR"):
        if employee.user_id != current_user.id:
            raise PermissionDeniedException("You do not have permission to view these documents")

    query = select(EmployeeDocument).where(and_(EmployeeDocument.employee_id == employee_id, EmployeeDocument.deleted_at.is_(None)))
    res = await db.execute(query)
    return list(res.scalars().all())

@router.get("/{id}/download", summary="Download employee document raw file")
async def download_document(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> FileResponse:
    query = select(EmployeeDocument).where(and_(EmployeeDocument.id == id, EmployeeDocument.deleted_at.is_(None)))
    res = await db.execute(query)
    doc = res.scalars().first()
    if not doc:
        raise EntityNotFoundException("Document metadata not found")

    # Security check: verify ownership
    emp_repo = EmployeeRepository(db)
    employee = await emp_repo.get_by_id(doc.employee_id)
    if not employee:
        raise EntityNotFoundException("Parent employee profile not found")
        
    if current_user.role not in ("SUPER_ADMIN", "ADMIN", "HR"):
        if employee.user_id != current_user.id:
            raise PermissionDeniedException("Access denied to download this file")

    if not os.path.exists(doc.file_path):
        raise EntityNotFoundException("Physical file not found on storage service disk")
        
    return FileResponse(
        path=doc.file_path,
        filename=doc.name,
        media_type=doc.mime_type
    )

@router.delete("/{id}", summary="Delete employee document")
async def delete_document(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    query = select(EmployeeDocument).where(and_(EmployeeDocument.id == id, EmployeeDocument.deleted_at.is_(None)))
    res = await db.execute(query)
    doc = res.scalars().first()
    if not doc:
        raise EntityNotFoundException("Document not found")
        
    emp_repo = EmployeeRepository(db)
    employee = await emp_repo.get_by_id(doc.employee_id)
    
    if current_user.role not in ("SUPER_ADMIN", "ADMIN", "HR"):
        if not employee or employee.user_id != current_user.id:
            raise PermissionDeniedException("Access denied to delete this document")

    storage = get_storage_service()
    await storage.delete_file(doc.file_path)
    
    # Soft delete in metadata
    doc.soft_delete()
    await db.commit()
    
    logger.info("document_deleted", doc_id=str(id))
    return {"success": True, "message": "Document deleted successfully"}
