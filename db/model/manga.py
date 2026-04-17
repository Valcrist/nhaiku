from sqlalchemy import Table
from db.common import (
    Base,
    Column,
    ForeignKey,
    Integer,
    BigInteger,
    String,
    Boolean,
    DateTime,
    func,
    relationship,
)
from db.relationships.manga import manga_tag, manga_related


# =============================================================================
# MANGA — Core manga entry
# =============================================================================


class Manga(Base):
    __tablename__ = "manga"
    id = Column(Integer, primary_key=True, index=True)
    media_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False, index=True)
    title_full = Column(String, nullable=False, index=True)
    title_jp = Column(String, nullable=True, index=True)
    cover = Column(String, nullable=True, index=True)
    thumbnail = Column(String, nullable=True, index=True)
    scanlator = Column(String, nullable=True, index=True)
    upload_date = Column(BigInteger, nullable=True, index=True)
    pages = Column(Integer, nullable=False, default=0, index=True)
    faves = Column(Integer, nullable=False, default=0, index=True)
    votes = Column(Integer, nullable=False, default=0, index=True)
    nuked = Column(Boolean, nullable=False, default=False, index=True)
    tags = relationship("Tag", secondary=manga_tag, backref="manga")
    page_list = relationship("Page", back_populates="manga")
    related = relationship(
        "Manga",
        secondary=manga_related,
        primaryjoin=lambda: Manga.id == manga_related.c.manga_id,
        secondaryjoin=lambda: Manga.id == manga_related.c.related_id,
    )
    created_at = Column(DateTime(timezone=True), default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), default=func.now(), index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)


# =============================================================================
# PAGE — Individual page within a manga
# =============================================================================


class Page(Base):
    __tablename__ = "page"
    id = Column(String, primary_key=True, index=True)  # "{manga_id}_{page_id}"
    manga_id = Column(Integer, ForeignKey("manga.id"), nullable=False, index=True)
    number = Column(Integer, nullable=False, index=True)
    url = Column(String, nullable=False, index=True)
    thumbnail = Column(String, nullable=False, index=True)
    img_name = Column(String, nullable=True, index=True)
    img_path = Column(String, nullable=True, index=True)
    manga = relationship("Manga", back_populates="page_list")


# =============================================================================
# TAG — Content tag (language, artist, character, etc.)
# =============================================================================


class Tag(Base):
    __tablename__ = "tag"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    slug = Column(String, nullable=False, unique=True, index=True)
    url = Column(String, nullable=False)
    count = Column(Integer, nullable=False, default=0, index=True)
