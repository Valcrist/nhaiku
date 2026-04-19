import asyncio
import httpx
from typing import Any
from core.exceptions import NHaikuError
from core.api_schema import CdnConfig, GalleryDetail, GalleryListItem, GalleryPage
from toolbox.utils import DEBUG, get_env, printc, varDump, debug


NH_URL = get_env("NH_URL", "https://nhentai.net/api/v2")
PER_PAGE_MAX = 100
_NH_KEY: str = get_env("NH_KEY", required=True)
_HEADERS = {
    "Authorization": f"Key {_NH_KEY}",
    "User-Agent": "nhaiku/1.0 (https://github.com/valcrist/nhaiku)",
}


def print_query(
    label: str, path: str, params: dict[str, Any] | None = None, lvl: int = 2
) -> None:
    if DEBUG < lvl or path in ["/cdn"]:
        return
    printc(f"[{label}]: {path}", "black", "yellow")
    if params:
        varDump(params, f"[{label}] params")


async def api_get(
    path: str, params: dict[str, Any] | None = None, retries: int = 10
) -> Any:
    print_query("api_get", path, params)
    url = f"{NH_URL}{path}"
    async with httpx.AsyncClient(headers=_HEADERS) as client:
        for attempt in range(retries + 1):
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 429 and attempt < retries:
                    delay = 2**attempt
                    printc(f"[api_get] Code 429: {path}", "bright_yellow")
                    printc(
                        f"[api_get] Retry: {attempt + 1} of {retries} [{delay}s]",
                        "bright_yellow",
                    )
                    await asyncio.sleep(delay)
                    continue
                raise NHaikuError(
                    f"Upstream API error {exc.response.status_code} for {path}:\n\n{exc}"
                )
            except httpx.RequestError as exc:
                raise NHaikuError(f"Request failed for {path}: {exc}")
            except Exception as exc:
                raise NHaikuError(f"Unexpected error for {path}: {exc}")


async def get_cdn() -> dict[str, Any]:
    data = await api_get("/cdn")
    return CdnConfig.model_validate(data).model_dump()


async def get_galleries(page: int = 1, per_page: int = 100) -> dict[str, Any]:
    per_page = min(per_page, PER_PAGE_MAX)
    data = await api_get("/galleries", params={"page": page, "per_page": per_page})
    return GalleryPage.model_validate({**data, "curr_page": page}).model_dump()


async def get_gallery(gallery_id: int) -> dict[str, Any]:
    data = await api_get(f"/galleries/{gallery_id}")
    resp = GalleryDetail.model_validate(data).model_dump()
    debug(resp, lvl=2)
    return resp


async def get_related_galleries(gallery_id: int) -> dict[str, Any]:
    data = await api_get(f"/galleries/{gallery_id}/related")
    result = [GalleryListItem.model_validate(item) for item in data["result"]]
    return {"result": [item.model_dump() for item in result]}
