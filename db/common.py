import uuid
from sqlalchemy import (
    cast,
    func,
    Index,
    Column,
    ForeignKey,
    CheckConstraint,
    Float,
    Integer,
    BigInteger,
    String,
    Boolean,
    Enum,
    DateTime,
    JSON,
    text,
)
from sqlalchemy.orm import (
    declarative_base,
    relationship,
    joinedload,
    aliased,
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy_utils import UUIDType
from toolbox.utils import get_env


# initialize
DB_URL = get_env("DB_URL", verbose=True)
DB_POOL_SIZE = get_env("DB_POOL_SIZE", 50, verbose=True)
DB_MAX_OVERFLOW = get_env("DB_MAX_OVERFLOW", 25, verbose=True)

_is_sqlite = DB_URL.startswith("sqlite")

engine: AsyncEngine = create_async_engine(
    DB_URL,
    echo=False,
    **(
        {}
        if _is_sqlite
        else {
            "pool_size": DB_POOL_SIZE,
            "max_overflow": DB_MAX_OVERFLOW,
            "pool_pre_ping": True,
            "pool_recycle": 1800,  # recycle before PgBouncer's server_lifetime (3600) kicks in
            "pool_timeout": 30,  # don't wait forever for a pool slot — fail fast
            "connect_args": {"server_settings": {"timezone": "UTC"}},
        }
    ),
)

dialect = engine.dialect.name
JsonType = JSONB if dialect == "postgresql" else JSON
Base = declarative_base()


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
