import uuid
from sqlalchemy import (
    create_engine,
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
    sessionmaker,
    scoped_session,
    declarative_base,
    relationship,
    joinedload,
    aliased,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import UUIDType
from toolbox.utils import get_env


# initialize
DB_URL = get_env("DB_URL", verbose=True)
DB_POOL_SIZE = get_env("DB_POOL_SIZE", 50, verbose=True)
DB_MAX_OVERFLOW = get_env("DB_MAX_OVERFLOW", 25, verbose=True)

_is_sqlite = DB_URL.startswith("sqlite")

engine = create_engine(
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
            "connect_args": {"options": "-c timezone=UTC"},
        }
    )
)

db_type = engine.name
dialect = engine.dialect.name
JsonType = JSONB if dialect == "postgresql" else JSON
Base = declarative_base()


def init_db():
    Base.metadata.create_all(bind=engine)
