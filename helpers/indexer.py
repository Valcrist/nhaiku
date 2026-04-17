from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from helpers.database import fetch_one, save_manga
from db.model.manga import Manga
from helpers.api_client import get_gallery
from toolbox.utils import err, debug


async def query_manga(id: int, session: AsyncSession | None = None) -> dict[str, Any]:
    return await fetch_one(select(Manga).where(Manga.id == id), session)


async def index_manga(id: int) -> dict[str, Any]:
    manga = await get_gallery(int(id))
    debug(manga)
    if manga:
        return await save_manga(manga)
    return {}


async def get_manga(id: int) -> dict[str, Any]:
    try:
        manga = await query_manga(int(id))
        if not manga:
            manga = await index_manga(int(id))
        return manga
    except Exception as e:
        err(f"Failed to get manga {id}: {e}")
        return {}
