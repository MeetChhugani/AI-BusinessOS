from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import RoleChecker
from app.database.session import get_db_session
from app.exceptions.custom_exceptions import EntityNotFoundException
from app.logging.config import logger
from app.models.hcm import Designation
from app.repositories.hcm_repository import DesignationRepository
from app.schemas.hcm import DesignationCreate, DesignationResponse

router = APIRouter(prefix="/designations", tags=["Designations"])

@router.get("", response_model=List[DesignationResponse], summary="List all designation ranks")
async def list_designations(
    db: AsyncSession = Depends(get_db_session)
) -> List[Designation]:
    des_repo = DesignationRepository(db)
    return await des_repo.get_all()

@router.post("", response_model=DesignationResponse, status_code=201, summary="Create a new designation rank")
async def create_designation(
    body: DesignationCreate,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "HR"])),
    db: AsyncSession = Depends(get_db_session),
) -> Designation:
    des_repo = DesignationRepository(db)
    new_des = Designation(
        name=body.name,
        hierarchy_level=body.hierarchy_level,
        department_id=body.department_id,
        salary_grade=body.salary_grade,
    )
    created = await des_repo.create(new_des)
    logger.info("designation_created", name=created.name)
    return created
