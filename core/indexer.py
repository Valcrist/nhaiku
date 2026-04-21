import asyncio
from typing import Any
from core.database import query_manga, save_manga
from core.api_client import get_gallery, NHaikuError
from core.download import download_art, download_pages
from core.error_logger import log_error
from db.global_enums import ErrorType
from toolbox.utils import err, debug, hr, printc


async def index_manga(id: int) -> dict[str, Any]:
    resp = await get_gallery(int(id))
    manga = await save_manga(resp)
    debug(manga, lvl=2)
    async with asyncio.TaskGroup() as tg:
        tg.create_task(download_art(manga, kind="cover"))
        tg.create_task(download_art(manga, kind="thumb"))
        tg.create_task(download_pages(manga["id"]))
    return manga


async def proc_manga(id: int, reindex: bool = False) -> dict[str, Any]:
    hr(no_nl=True)
    printc(f"Getting manga {id} ..\n", "bright_magenta")
    try:
        manga = None if reindex else await query_manga(int(id))
        if not manga:
            await index_manga(int(id))
            manga = await query_manga(int(id))
        return manga
    except NHaikuError as e:
        await log_error(
            location="indexer.proc_manga",
            remark=f"API error while processing manga {id}",
            error_type=ErrorType.api_error,
            exc=e,
            manga_id=id,
        )
    except Exception as e:
        err(f"Failed to get manga {id}: {e}")
        await log_error(
            location="indexer.proc_manga",
            remark=f"Unexpected error while processing manga {id}",
            error_type=ErrorType.unknown,
            exc=e,
            manga_id=id,
        )
    return {}
