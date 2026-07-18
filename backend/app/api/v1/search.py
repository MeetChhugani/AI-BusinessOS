from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user
from app.database.session import get_db_session
from app.services.platform_service import SearchService
from app.schemas.platform import SearchIndexResponse

router = APIRouter(prefix="/search", tags=["Global Search Engine"])

@router.get("", response_model=List[SearchIndexResponse], summary="Perform unified keyword global search")
async def global_search(
    q: str = Query(..., min_length=2),
    db: AsyncSession = Depends(get_db_session)
):
    return await SearchService.search_query(db, q)
