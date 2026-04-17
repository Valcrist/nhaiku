from sqlalchemy import Table
from db.common import (
    Base,
    Column,
    ForeignKey,
    Integer,
    String,
)


# =============================================================================
# MANGA_TAG — Many-to-many between Manga and Tag
# =============================================================================


manga_tag = Table(
    "manga_tag",
    Base.metadata,
    Column("manga_id", Integer, ForeignKey("manga.id"), primary_key=True, index=True),
    Column("manga_title", String, nullable=False, index=True),
    Column("tag_id", Integer, ForeignKey("tag.id"), primary_key=True, index=True),
    Column("tag_type", String, nullable=False, index=True),
    Column("tag_slug", String, nullable=False, index=True),
)


# =============================================================================
# MANGA_RELATED — Self-referential many-to-many for related manga
# =============================================================================


manga_related = Table(
    "manga_related",
    Base.metadata,
    Column("manga_id", Integer, ForeignKey("manga.id"), primary_key=True, index=True),
    Column("manga_title", String, nullable=False, index=True),
    Column("related_id", Integer, ForeignKey("manga.id"), primary_key=True, index=True),
    Column("related_title", String, nullable=False, index=True),
)
