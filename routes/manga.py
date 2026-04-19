from typing import Union, Dict, Any
from fastapi import APIRouter, Depends, Request, BackgroundTasks
from db.model.manga import Manga
from db.schema.manga import MangaSchema
from core.indexer import proc_manga
from core.exceptions import LoggedHTTPException
from toolbox.date import utc_now
from toolbox.utils import err, warn, debug


router = APIRouter(
    prefix="/manga",
    tags=["manga"],
)


@router.get("/{manga_id:int}")
async def get_manga(manga_id: int):
    return await proc_manga(manga_id)


@router.get("/reindex/{manga_id:int}")
async def reindex_manga(manga_id: int):
    return await proc_manga(manga_id, reindex=True)
