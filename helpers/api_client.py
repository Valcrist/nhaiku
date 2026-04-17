import httpx
from typing import Any
from helpers.exceptions import NHaikuError
from helpers.api_schema import GalleryDetail, GalleryListItem, GalleryPage
from toolbox.utils import get_env, printc, varDump


NH_URL = "https://nhentai.net/api/v2"
_NH_KEY: str = get_env("NH_KEY") or ""
if not _NH_KEY:
    raise NHaikuError("NH_KEY environment variable is not set")
_HEADERS = {
    "Authorization": f"Key {_NH_KEY}",
    "User-Agent": "nhaiku/1.0 (https://github.com/valcrist/nhaiku)",
}

PER_PAGE_MAX = 100


def print_query(label: str, path: str, params: dict[str, Any] | None = None) -> None:
    printc(f"[{label}]: {path}", "black", "yellow")
    if params:
        varDump(params, f"[{label}] params")


async def api_get(path: str, params: dict[str, Any] | None = None) -> Any:
    print_query("api_get", path, params)
    url = f"{NH_URL}{path}"
    async with httpx.AsyncClient(headers=_HEADERS) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise NHaikuError(
                f"Upstream API error {exc.response.status_code} for {path}"
            ).add_note(exc.response.text) from exc
        except httpx.RequestError as exc:
            raise NHaikuError(f"Request failed for {path}") from exc


async def get_galleries(page: int = 1, per_page: int = 100) -> dict[str, Any]:
    per_page = min(per_page, PER_PAGE_MAX)
    data = await api_get("/galleries", params={"page": page, "per_page": per_page})
    return GalleryPage.model_validate({**data, "curr_page": page}).model_dump()


async def get_gallery(gallery_id: int) -> dict[str, Any]:
    data = await api_get(f"/galleries/{gallery_id}")
    return GalleryDetail.model_validate(data).model_dump()


async def get_related_galleries(gallery_id: int) -> dict[str, Any]:
    data = await api_get(f"/galleries/{gallery_id}/related")
    result = [GalleryListItem.model_validate(item) for item in data["result"]]
    return {"result": [item.model_dump() for item in result]}
