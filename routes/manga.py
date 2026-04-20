from fastapi import APIRouter
from pydantic import BaseModel
from db.schema.manga import MangaResponse
from core.indexer import proc_manga
from core.api_client import SearchSort, WHITELIST, BLACKLIST, search_galleries
from core.api_schema import GalleryPage
from toolbox.utils import err, warn, debug


router = APIRouter(
    prefix="/manga",
    tags=["manga"],
)


class SearchRequest(BaseModel):
    query: list[str] = []
    sort: SearchSort = "date"
    page: int = 1
    whitelist: list[str] | None = WHITELIST
    blacklist: list[str] | None = BLACKLIST


@router.get("/{manga_id:int}", response_model=MangaResponse)
async def get_manga(manga_id: int):
    return await proc_manga(manga_id)


@router.get("/reindex/{manga_id:int}", response_model=MangaResponse)
async def reindex_manga(manga_id: int):
    return await proc_manga(manga_id, reindex=True)


@router.post("/search", response_model=GalleryPage)
async def search_manga(body: SearchRequest):
    return await search_galleries(
        body.query, body.sort, body.page, body.whitelist, body.blacklist
    )
