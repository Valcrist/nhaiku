import httpx
import asyncio
from typing import Any
from datetime import datetime
from imgroyale import dedupe_image
from core.api_client import get_cdn
from core.database import update_manga, update_page, get_missing_pages
from core.exceptions import NHaikuError
from core.constants import SCRATCH_DIR, COVER_DIR, THUMB_DIR, IMAGE_DIR
from toolbox.date import utc_now, time_delta
from toolbox.fs import (
    join_path,
    os_path,
    slash_nix,
    path_exists,
    dirname,
    basename,
    barename,
    delete,
)
from toolbox.utils import DEBUG, get_env, printc, varDump, debug, warn


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


def cleanup(path: str) -> None:
    delete(os_path(path))
    delete(os_path(f"{dirname(path)}/{barename(path)}.webp"))


async def download_pages(manga_id: int) -> list[dict[str, Any]]:
    pages = await get_missing_pages(manga_id)
    if not pages:
        return []

    files: list[tuple[str, str]] = []
    for page in pages:
        server = await get_server(is_thumb=False)
        url = f"{server.rstrip('/')}/{page['url']}"
        dest = join_path(SCRATCH_DIR, f"{manga_id}_{basename(page['url'])}")
        files.append((url, dest))

    downloaded = await download_files(files)
    page_files: list[str] = []
    for scratch_path in downloaded:
        page_path = dedupe_image(scratch_path, IMAGE_DIR, SCRATCH_DIR)
        page_file = slash_nix(page_path).removeprefix(slash_nix(IMAGE_DIR)).lstrip("/")
        page_files.append(page_file)
        cleanup(scratch_path)

    results = await asyncio.gather(
        *[update_page(p["id"], {"page_file": pf}) for p, pf in zip(pages, page_files)]
    )
    return list(results)


async def download_art(manga: dict[str, Any], kind: str = "cover") -> str:
    art_map = {
        "cover": (COVER_DIR, "cover", "cover_file"),
        "thumb": (THUMB_DIR, "thumbnail", "thumbnail_file"),
    }
    if kind not in art_map:
        raise ValueError(f"kind must be 'cover' or 'thumb', got {kind!r}")
    dest_dir, key, field = art_map[kind]
    if manga.get(f"{key}_file"):
        return manga[f"{key}_file"]
    server = await get_server(is_thumb=True)
    media_id = manga["media_id"]
    url = f"{server.rstrip('/')}/{manga[key]}"
    scratch = join_path(SCRATCH_DIR, f"{media_id}_{basename(manga[key])}")
    (path,) = await download_files([(url, scratch)])
    result = dedupe_image(path, dest_dir, SCRATCH_DIR)
    art_file = slash_nix(result).removeprefix(slash_nix(dest_dir)).lstrip("/")
    cleanup(path)
    await update_manga(manga["id"], {field: art_file}, session=None)
    return art_file
