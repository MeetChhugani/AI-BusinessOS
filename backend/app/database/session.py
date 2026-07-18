from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.config.settings import settings

# Configure connection pooling and timeout management for PostgreSQL
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=20,          # Standard pool size
    max_overflow=10,       # Allow burst connections
    pool_recycle=1800,     # Recycle connection every 30 minutes
    pool_pre_ping=True,    # Check validity before using
)

async_session_maker = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injector for database sessions."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
