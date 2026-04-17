from typing import Any
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from db.common import Base
from db.session import AsyncSessionLocal


def model_to_dict(obj: Base) -> dict[str, Any]:
    return {col.name: getattr(obj, col.name) for col in obj.__table__.columns}


async def fetch_one(stmt: Any, session: AsyncSession | None = None) -> dict[str, Any]:
    async def _run(s: AsyncSession) -> dict[str, Any]:
        try:
            result = await s.execute(stmt)
            row = result.scalar_one_or_none()
            return model_to_dict(row) if row is not None else {}
        except:
            raise

    if session is not None:
        return await _run(session)
    async with AsyncSessionLocal() as s:
        return await _run(s)
