from fastapi import APIRouter
from pydantic import BaseModel
from db.schema.manga import MangaResponse
from core.indexer import proc_manga
from core.database import LocalSearchSort, search_manga
from core.api_client import RemoteSearchSort, search_galleries
from core.api_schema import GalleryPage


router = APIRouter(
    prefix="/manga",
    tags=["manga"],
)


class LocalSearchRequest(BaseModel):
    query: list[str] = []
    sort: LocalSearchSort = "date"
    page: int = 1


class RemoteSearchRequest(BaseModel):
    query: list[str] = []
    sort: RemoteSearchSort = "date"
    page: int = 1


@router.get("/{manga_id:int}", response_model=MangaResponse)
async def get_manga(manga_id: int):
    return await proc_manga(manga_id)


@router.get("/reindex/{manga_id:int}", response_model=MangaResponse)
async def reindex_manga(manga_id: int):
    return await proc_manga(manga_id, reindex=True)


@router.post("/local/search", response_model=GalleryPage)
async def local_search_manga(body: LocalSearchRequest):
    return await search_manga(body.query, body.sort, body.page)


@router.post("/remote/search", response_model=GalleryPage)
async def remote_search_manga(body: RemoteSearchRequest):
    return await search_galleries(body.query, body.sort, body.page)
