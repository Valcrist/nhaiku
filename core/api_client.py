import asyncio
import httpx
from typing import Any, Literal
from core.exceptions import NHaikuError
from core.api_schema import CdnConfig, GalleryDetail, GalleryListItem, GalleryPage
from toolbox.utils import DEBUG, get_env, printc, varDump, debug


SearchSort = Literal[
    "date", "popular", "popular-today", "popular-week", "popular-month"
]

WHITELIST: list[str] = [
    "language:english",
]

BLACKLIST: list[str] = [
    'tag:"yaoi"',
    'tag:"males-only"',
    'tag:"mmm-threesome"',
    'tag:"dickgirl-on-male"',
    'tag:"gender-bender"',
]


NH_URL = get_env("NH_URL", "https://nhentai.net/api/v2")
PER_PAGE_MAX = 100
_NH_KEY: str = get_env("NH_KEY", required=True)
_HEADERS = {
    "Authorization": f"Key {_NH_KEY}",
    "User-Agent": "nhaiku/0.1.1 (https://github.com/valcrist/nhaiku)",
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
                code = exc.response.status_code
                if attempt < retries:
                    delay = 2**attempt
                    printc(f"[api_get] Response code {code}: {path}", "bright_yellow")
                    printc(
                        f"[api_get] Retry: {attempt + 1} of {retries} [{delay}s]",
                        "bright_yellow",
                    )
                    await asyncio.sleep(delay)
                    continue
                raise NHaikuError(f"Upstream API error {code} for {path}:\n\n{exc}")
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


async def search_galleries(
    query: list[str] = [],
    sort: SearchSort = "date",
    page: int = 1,
    whitelist: list[str] = WHITELIST,
    blacklist: list[str] = BLACKLIST,
) -> dict[str, Any]:
    terms = dict.fromkeys(t for t in query if t.strip())
    query_bases = {t.lstrip("-") for t in terms}
    for t in whitelist:
        if t.lstrip("-") not in query_bases:
            terms.setdefault(t, None)
    for t in blacklist:
        if t not in query_bases:
            terms.setdefault(f"-{t}", None)
    debug(terms, lvl=2)
    full_query = " ".join(terms)
    debug(full_query, lvl=2)
    data = await api_get(
        "/search",
        params={"query": full_query.strip(), "sort": sort, "page": page},
    )
    debug(data, lvl=2)
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
