from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import RoleChecker, get_current_user
from app.database.session import get_db_session
from app.exceptions.custom_exceptions import EntityNotFoundException, ValidationException
from app.logging.config import logger
from app.models.inventory import (
    Product,
    ProductCategory,
    ProductVariant,
    ProductImage,
    ProductSerial,
    ProductTimeline,
    Unit,
)
from app.repositories.inventory_repository import ProductRepository
from app.schemas.inventory import (
    ProductCategoryCreate,
    ProductCategoryResponse,
    ProductCreate,
    ProductResponse,
    ProductVariantCreate,
    ProductVariantResponse,
)

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("", response_model=List[ProductResponse], summary="List product catalog catalog")
async def list_products(
    search: Optional[str] = None,
    category_id: Optional[UUID] = None,
    brand: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
) -> List[Product]:
    repo = ProductRepository(db)
    products, _ = await repo.get_all_paginated(
        search=search,
        category_id=category_id,
        brand=brand,
        status=status,
        skip=skip,
        limit=limit,
    )
    return products

@router.post("", response_model=ProductResponse, status_code=201, summary="Create a new product profile")
async def create_product(
    body: ProductCreate,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "INVENTORY_MANAGER"])),
    db: AsyncSession = Depends(get_db_session)
) -> Product:
    new_prod = Product(
        sku=body.sku,
        barcode=body.barcode,
        qr_code=body.qr_code,
        name=body.name,
        description=body.description,
        category_id=body.category_id,
        brand=body.brand,
        cost_price=body.cost_price,
        selling_price=body.selling_price,
        tax_rate=body.tax_rate,
        weight=body.weight,
        dimensions=body.dimensions,
        unit_id=body.unit_id,
        status=body.status,
    )
    db.add(new_prod)
    await db.flush() # get id
    
    # Save images
    if body.images:
        for img in body.images:
            p_img = ProductImage(
                product_id=new_prod.id,
                image_url=img.image_url,
                is_primary=img.is_primary,
                thumbnail_url=img.thumbnail_url
            )
            db.add(p_img)
            
    # Track created timeline event
    tl = ProductTimeline(
        product_id=new_prod.id,
        event_type="CREATED",
        description=f"Product profile initialized with SKU {body.sku}"
    )
    db.add(tl)
    await db.commit()
    await db.refresh(new_prod)
    logger.info("product_created", sku=new_prod.sku)
    return new_prod

@router.get("/categories", response_model=List[ProductCategoryResponse], summary="List nested categories")
async def list_categories(
    db: AsyncSession = Depends(get_db_session)
) -> List[ProductCategory]:
    query = select(ProductCategory).where(ProductCategory.deleted_at.is_(None))
    res = await db.execute(query.order_by(ProductCategory.name))
    return list(res.scalars().all())

@router.post("/categories", response_model=ProductCategoryResponse, status_code=201, summary="Create category")
async def create_category(
    body: ProductCategoryCreate,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "INVENTORY_MANAGER"])),
    db: AsyncSession = Depends(get_db_session)
) -> ProductCategory:
    cat = ProductCategory(
        name=body.name,
        code=body.code,
        description=body.description,
        parent_id=body.parent_id,
        icon=body.icon,
        status=body.status
    )
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return cat

@router.post("/variants", response_model=ProductVariantResponse, status_code=201, summary="Create variant")
async def create_variant(
    body: ProductVariantCreate,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "INVENTORY_MANAGER"])),
    db: AsyncSession = Depends(get_db_session)
) -> ProductVariant:
    variant = ProductVariant(
        product_id=body.product_id,
        sku=body.sku,
        barcode=body.barcode,
        name=body.name,
        cost_price=body.cost_price,
        selling_price=body.selling_price,
        attribute_values=body.attribute_values,
        status=body.status
    )
    db.add(variant)
    
    # Track Variant creation in Product timeline
    tl = ProductTimeline(
        product_id=body.product_id,
        event_type="PRICE_CHANGED",
        description=f"Variant '{body.name}' with SKU '{body.sku}' added."
    )
    db.add(tl)
    await db.commit()
    await db.refresh(variant)
    return variant

@router.get("/{id}/timeline", summary="Get product timeline logs")
async def get_product_timeline(
    id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    query = select(ProductTimeline).where(ProductTimeline.product_id == id).order_by(ProductTimeline.event_date.desc())
    res = await db.execute(query)
    return list(res.scalars().all())
