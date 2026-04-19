from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime


# -------------------------------------------------------------------------------------
# Manga
# -------------------------------------------------------------------------------------


class MangaBase(BaseModel):
    media_id: str
    title: str
    title_full: str
    title_jp: Optional[str] = None
    cover: Optional[str] = None
    cover_file: Optional[str] = None
    thumbnail: Optional[str] = None
    thumbnail_file: Optional[str] = None
    scanlator: Optional[str] = None
    upload_date: Optional[int] = None
    pages: int = 0
    faves: int = 0
    votes: int = 0
    nuked: bool = False


class MangaCreate(MangaBase):
    pass


class MangaSchema(MangaBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class MangaUpdate(BaseModel):
    media_id: Optional[str] = None
    title: Optional[str] = None
    title_full: Optional[str] = None
    title_jp: Optional[str] = None
    cover: Optional[str] = None
    cover_file: Optional[str] = None
    thumbnail: Optional[str] = None
    thumbnail_file: Optional[str] = None
    scanlator: Optional[str] = None
    upload_date: Optional[int] = None
    pages: Optional[int] = None
    faves: Optional[int] = None
    votes: Optional[int] = None
    nuked: Optional[bool] = None


# -------------------------------------------------------------------------------------
# Page
# -------------------------------------------------------------------------------------


class PageBase(BaseModel):
    id: str  # "{manga_id}_{page_id}"
    manga_id: int
    number: int
    url: str
    page_file: Optional[str] = None


class PageCreate(PageBase):
    pass


class PageSchema(PageBase):
    model_config = ConfigDict(from_attributes=True)


class PageUpdate(BaseModel):
    number: Optional[int] = None
    url: Optional[str] = None
    page_file: Optional[str] = None


# -------------------------------------------------------------------------------------
# MangaRelated
# -------------------------------------------------------------------------------------


class MangaRelatedCreate(BaseModel):
    manga_id: int
    manga_title: str
    related_id: int
    related_title: str


# -------------------------------------------------------------------------------------
# Tag
# -------------------------------------------------------------------------------------


class TagBase(BaseModel):
    type: str
    name: str
    slug: str
    url: str
    count: int = 0


class TagCreate(TagBase):
    id: int


class TagSchema(TagBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class TagUpdate(BaseModel):
    type: Optional[str] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    url: Optional[str] = None
    count: Optional[int] = None


# -------------------------------------------------------------------------------------
# MangaTag
# -------------------------------------------------------------------------------------


class MangaTagCreate(BaseModel):
    manga_id: int
    manga_title: str
    tag_id: int
    tag_type: str
    tag_slug: str


# -------------------------------------------------------------------------------------
# MangaResponse — shaped API response with nested tags and pages
# -------------------------------------------------------------------------------------


class TagResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    type: str
    slug: str


class PageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    number: int
    page_file: Optional[str] = None


class MangaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    media_id: str
    title: str
    title_full: str
    title_jp: Optional[str] = None
    cover_file: Optional[str] = None
    thumbnail_file: Optional[str] = None
    scanlator: Optional[str] = None
    pages: int
    votes: int
    tags: list[TagResponse] = []
    page_list: list[PageResponse] = []

    @field_validator("tags", mode="after")
    @classmethod
    def sort_tags(cls, v: list[TagResponse]) -> list[TagResponse]:
        return sorted(v, key=lambda t: (t.type, t.slug))

    @field_validator("page_list", mode="after")
    @classmethod
    def sort_pages(cls, v: list[PageResponse]) -> list[PageResponse]:
        return sorted(v, key=lambda p: p.number)
