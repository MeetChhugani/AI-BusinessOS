import asyncio
import os
from collections.abc import AsyncGenerator
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Force ENVIRONMENT to testing so Pydantic Settings loads .env.test
os.environ["ENVIRONMENT"] = "testing"

from app.config.settings import settings
from app.database.session import get_db_session
from app.main import app
from app.models.base import Base
from app.services.redis_service import redis_service

# Create testing engine
test_engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)

test_session_maker = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db() -> AsyncGenerator[None, None]:
    """Drops and recreates test database tables before running tests."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize redis service client for tests
    redis_service.connect()
    
    yield
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await redis_service.disconnect()
    await test_engine.dispose()

@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Asynchronous session context fixture."""
    async with test_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Asynchronous HTTP Client with overridden database dependencies."""
    async def _get_db_session_override() -> AsyncGenerator[AsyncSession, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db_session] = _get_db_session_override
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
