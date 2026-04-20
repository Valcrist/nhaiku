from typing import Union, Dict, Any
from fastapi import APIRouter, Depends, Request, BackgroundTasks
from pydantic import BaseModel
from db.model.manga import Manga
from db.schema.manga import MangaSchema
from core.indexer import proc_manga
from core.exceptions import LoggedHTTPException
from core.api_client import SearchSort, WHITELIST, BLACKLIST, search_galleries
from toolbox.date import utc_now
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


@router.get("/{manga_id:int}")
async def get_manga(manga_id: int):
    return await proc_manga(manga_id)


@router.get("/reindex/{manga_id:int}")
async def reindex_manga(manga_id: int):
    return await proc_manga(manga_id, reindex=True)


@router.post("/search")
async def search_manga(body: SearchRequest):
    return await search_galleries(
        body.query, body.sort, body.page, body.whitelist, body.blacklist
    )
