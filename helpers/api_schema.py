from pydantic import BaseModel


class GalleryListItem(BaseModel):
    id: int
    media_id: str
    english_title: str
    japanese_title: str | None = None
    thumbnail: str
    thumbnail_width: int
    thumbnail_height: int
    num_pages: int = 0
    tag_ids: list[int] = []
    blacklisted: bool = False


class GalleryPage(BaseModel):
    result: list[GalleryListItem]
    curr_page: int
    num_pages: int


class GalleryTitle(BaseModel):
    english: str
    japanese: str | None = None
    pretty: str


class CoverInfo(BaseModel):
    path: str
    width: int
    height: int


class TagResponse(BaseModel):
    id: int
    type: str
    name: str
    slug: str
    url: str
    count: int


class PageInfo(BaseModel):
    number: int
    path: str
    width: int
    height: int
    thumbnail: str
    thumbnail_width: int
    thumbnail_height: int


class CdnConfig(BaseModel):
    image_servers: list[str]
    thumb_servers: list[str]


class GalleryDetail(BaseModel):
    id: int
    media_id: str
    title: GalleryTitle
    cover: CoverInfo
    thumbnail: CoverInfo
    scanlator: str = ""
    upload_date: int
    tags: list[TagResponse]
    num_pages: int
    num_favorites: int
    pages: list[PageInfo] = []
    related: list[GalleryListItem] | None = None
    is_favorited: bool | None = None
