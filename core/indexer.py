from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import fetch_one, save_manga
from db.model.manga import Manga
from core.api_client import get_gallery, NHaikuError
from core.download import download_cover
from toolbox.utils import err, debug, hr, printc


async def query_manga(id: int, session: AsyncSession | None = None) -> dict[str, Any]:
    return await fetch_one(select(Manga).where(Manga.id == id), session)


async def index_manga(id: int) -> dict[str, Any]:
    resp = await get_gallery(int(id))
    manga = await save_manga(resp)
    debug(manga, lvl=2)
    cover, thumb = await download_cover(manga)
    debug(cover, lvl=2)
    debug(thumb, lvl=2)
    return manga


async def get_manga(id: int, reindex: bool = False) -> dict[str, Any]:
    hr(no_nl=True)
    printc(f"Getting manga {id} ..\n", "bright_magenta")
    try:
        manga = None if reindex else await query_manga(int(id))
        if not manga:
            manga = await index_manga(int(id))
        return manga
    except NHaikuError:
        pass
    except Exception as e:
        err(f"Failed to get manga {id}: {e}")
    return {}
