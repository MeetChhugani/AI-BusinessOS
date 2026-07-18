from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import RoleChecker
from app.database.session import get_db_session
from app.exceptions.custom_exceptions import EntityNotFoundException
from app.logging.config import logger
from app.models.inventory import Warehouse, WarehouseLocation, Inventory
from app.schemas.inventory import (
    WarehouseCreate,
    WarehouseResponse,
)

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])

@router.get("", response_model=List[WarehouseResponse], summary="List all warehouses")
async def list_warehouses(
    db: AsyncSession = Depends(get_db_session)
) -> List[Warehouse]:
    query = select(Warehouse).where(Warehouse.deleted_at.is_(None))
    result = await db.execute(query.order_by(Warehouse.name))
    return list(result.scalars().all())

@router.post("", response_model=WarehouseResponse, status_code=201, summary="Create a new warehouse")
async def create_warehouse(
    body: WarehouseCreate,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "HR", "INVENTORY_MANAGER"])),
    db: AsyncSession = Depends(get_db_session)
) -> Warehouse:
    new_wh = Warehouse(
        name=body.name,
        code=body.code,
        address=body.address,
        capacity=body.capacity,
        status=body.status,
        manager_id=body.manager_id,
    )
    db.add(new_wh)
    await db.commit()
    await db.refresh(new_wh)
    logger.info("warehouse_created", name=new_wh.name, code=new_wh.code)
    return new_wh

@router.get("/locations", summary="List warehouse location bins")
async def list_locations(
    warehouse_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    query = select(WarehouseLocation).where(
        and_(
            WarehouseLocation.warehouse_id == warehouse_id,
            WarehouseLocation.deleted_at.is_(None)
        )
    )
    result = await db.execute(query)
    return list(result.scalars().all())

@router.post("/locations", status_code=201, summary="Create a warehouse location bin")
async def create_location(
    warehouse_id: UUID,
    zone: str,
    rack: str,
    shelf: str,
    bin: str,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "INVENTORY_MANAGER", "WAREHOUSE_MANAGER"])),
    db: AsyncSession = Depends(get_db_session)
):
    code = f"LOC-{zone}-{rack}-{shelf}-{bin}".upper()
    loc = WarehouseLocation(
        warehouse_id=warehouse_id,
        zone=zone,
        rack=rack,
        shelf=shelf,
        bin=bin,
        code=code
    )
    db.add(loc)
    await db.commit()
    await db.refresh(loc)
    logger.info("location_bin_created", code=code)
    return loc

@router.get("/stats", summary="Get warehouse capacities and utilization stats")
async def get_warehouse_stats(
    db: AsyncSession = Depends(get_db_session)
):
    # Fetch warehouses and sum up inventory items
    query = select(Warehouse).where(Warehouse.deleted_at.is_(None))
    res = await db.execute(query)
    warehouses = res.scalars().all()
    
    stats = []
    for wh in warehouses:
        inv_query = select(func.sum(Inventory.quantity_on_hand)).where(Inventory.warehouse_id == wh.id)
        inv_res = await db.execute(inv_query)
        total_items = inv_res.scalar() or 0.0
        
        utilization = (total_items / wh.capacity * 100.0) if wh.capacity > 0 else 0.0
        stats.append({
            "id": str(wh.id),
            "name": wh.name,
            "code": wh.code,
            "capacity": wh.capacity,
            "utilization": round(utilization, 2),
            "total_items": total_items
        })
    return stats
from sqlalchemy import and_
