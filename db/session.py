from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from db.common import engine


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
