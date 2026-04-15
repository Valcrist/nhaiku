from db.common import (
    Base,
    Column,
    uuid,
    UUIDType,
    String,
    DateTime,
    func,
)


# =============================================================================
# USER — Core user account
# =============================================================================


class User(Base):
    __tablename__ = "user"
    id = Column(
        UUIDType(binary=False),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    auth0_id = Column(String, unique=True, nullable=True, index=True)
    email = Column(String, unique=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), default=func.now(), index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)
