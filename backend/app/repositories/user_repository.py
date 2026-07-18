from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, user_id: UUID, include_deleted: bool = False) -> Optional[User]:
        query = select(User).where(User.id == user_id)
        if not include_deleted:
            query = query.where(User.deleted_at.is_(None))
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_by_email(self, email: str, include_deleted: bool = False) -> Optional[User]:
        query = select(User).where(User.email == email)
        if not include_deleted:
            query = query.where(User.deleted_at.is_(None))
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user: User) -> User:
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def soft_delete(self, user: User) -> User:
        user.soft_delete()
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def restore(self, user: User) -> User:
        user.restore()
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_all_active(self) -> List[User]:
        query = select(User).where(User.deleted_at.is_(None))
        result = await self.db.execute(query)
        return list(result.scalars().all())
