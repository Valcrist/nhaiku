import httpx
import asyncio
from typing import Any
from datetime import datetime

from imgroyale import dedupe_image
from core.api_client import get_cdn
from core.exceptions import NHaikuError
from core.constants import SCRATCH_DIR, COVER_DIR, THUMB_DIR, IMAGE_DIR
from toolbox.date import utc_now, time_delta
from toolbox.fs import join_path, basename, path_exists, slash_nix
from toolbox.utils import DEBUG, get_env, printc, varDump, debug


CONCURRENT_DL = get_env("CONCURRENT_DL", 5, verbose=1)

_CDN_TTL = 7200  # 2 hours
_cdn: dict[str, Any] = {}
_cdn_fetched_at: datetime | None = None
_image_idx: int = 0
_thumb_idx: int = 0


async def ensure_cdn() -> None:
    global _cdn, _cdn_fetched_at
    if not _cdn_fetched_at or time_delta(_cdn_fetched_at) > _CDN_TTL:
        _cdn = await get_cdn()
        _cdn_fetched_at = utc_now()


async def get_server(is_thumb: bool = False) -> str:
    global _image_idx, _thumb_idx
    await ensure_cdn()
    if is_thumb:
        servers = _cdn["thumb_servers"]
        url = servers[_thumb_idx % len(servers)]
        _thumb_idx += 1
    else:
        servers = _cdn["image_servers"]
        url = servers[_image_idx % len(servers)]
        _image_idx += 1
    return url


async def _fetch_file(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    url: str,
    dest: str,
    redownload: bool = False,
) -> str:
    if not redownload and path_exists(dest):
        return dest
    async with sem:
        printc(f"Downloading: {url} to {dest} ..\n", "yellow")
        resp = await client.get(url)
        resp.raise_for_status()
        with open(dest, "wb") as f:
            f.write(resp.content)
    return dest


async def download_files(
    files: list[tuple[str, str]], redownload: bool = False
) -> list[str]:
    sem = asyncio.Semaphore(CONCURRENT_DL)
    try:
        async with httpx.AsyncClient() as client:
            async with asyncio.TaskGroup() as tg:
                tasks = [
                    tg.create_task(_fetch_file(client, sem, url, dest, redownload))
                    for url, dest in files
                ]
    except* httpx.HTTPError as eg:
        eg.add_note(f"Failed to download {len(files)} file(s)")
        raise
    return [t.result() for t in tasks]


async def download_cover(manga: dict[str, Any]) -> tuple[str, str]:
    cover_server, thumb_server = await asyncio.gather(
        get_server(is_thumb=True),
        get_server(is_thumb=True),
    )
    media_id = manga["media_id"]
    files = [
        (
            f"{cover_server.rstrip('/')}/{manga['cover']}",
            join_path(SCRATCH_DIR, f"{media_id}_{basename(manga['cover'])}"),
        ),
        (
            f"{thumb_server.rstrip('/')}/{manga['thumbnail']}",
            join_path(SCRATCH_DIR, f"{media_id}_{basename(manga['thumbnail'])}"),
        ),
    ]
    cover_path, thumb_path = await download_files(files)
    cover_file = dedupe_image(cover_path, COVER_DIR, SCRATCH_DIR)
    cover_file = slash_nix(cover_file).removeprefix(slash_nix(COVER_DIR)).lstrip("/")
    thumb_file = dedupe_image(thumb_path, THUMB_DIR, SCRATCH_DIR)
    thumb_file = slash_nix(thumb_file).removeprefix(slash_nix(THUMB_DIR)).lstrip("/")
    return cover_file, thumb_file
