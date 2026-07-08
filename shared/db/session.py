import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# For standalone, default to localhost. Services can override this.
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/testlens")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=int(os.environ.get("DB_POOL_SIZE", 50)),
    max_overflow=int(os.environ.get("DB_MAX_OVERFLOW", 100))
)

async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db_session():
    async with async_session_maker() as session:
        yield session
