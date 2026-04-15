from typing import Optional
from pydantic import BaseModel, ConfigDict
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
    thumbnail: Optional[str] = None
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
    thumbnail: Optional[str] = None
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
    img_name: str
    img_path: str


class PageCreate(PageBase):
    pass


class PageSchema(PageBase):
    model_config = ConfigDict(from_attributes=True)


class PageUpdate(BaseModel):
    img_name: Optional[str] = None
    img_path: Optional[str] = None
