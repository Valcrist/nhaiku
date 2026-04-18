from typing import Any
from collections.abc import Callable, Coroutine
from sqlalchemy import delete, insert, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from db.common import Base
from db.model.manga import Manga, Page, Tag
from db.relationships.manga import manga_tag
from db.session import AsyncSessionLocal
from toolbox.utils import DEBUG, printc, debug


type _Runner[T] = Callable[[AsyncSession], Coroutine[Any, Any, T]]


def model_to_dict(obj: Base) -> dict[str, Any]:
    return {col.name: getattr(obj, col.name) for col in obj.__table__.columns}


async def _run_with_session[T](fn: _Runner[T], session: AsyncSession | None) -> T:
    if session is not None:
        return await fn(session)
    async with AsyncSessionLocal() as s:
        return await fn(s)


async def fetch_one(stmt: Any, session: AsyncSession | None = None) -> dict[str, Any]:
    async def _run(s: AsyncSession) -> dict[str, Any]:
        1 / 0
        result = await s.execute(stmt)
        row = result.scalar_one_or_none()
        return model_to_dict(row) if row is not None else {}

    return await _run_with_session(_run, session)


async def save_manga(
    data: dict[str, Any], session: AsyncSession | None = None
) -> dict[str, Any]:
    async def _run(s: AsyncSession) -> dict[str, Any]:
        printc(
            f"Saving [{data['id']}] {data['title']['pretty']} ..",
            "black",
            "bright_green",
        )
        async with s.begin():
            manga = await s.merge(
                Manga(
                    id=data["id"],
                    media_id=data["media_id"],
                    title=data["title"]["pretty"],
                    title_full=data["title"]["english"],
                    title_jp=data["title"].get("japanese"),
                    cover=(data.get("cover") or {}).get("path"),
                    thumbnail=(data.get("thumbnail") or {}).get("path"),
                    scanlator=data.get("scanlator"),
                    upload_date=data.get("upload_date"),
                    pages=data.get("num_pages", 0),
                    faves=data.get("num_favorites", 0),
                )
            )
            for t in data.get("tags", []):
                await s.merge(
                    Tag(
                        id=t["id"],
                        type=t["type"],
                        name=t["name"],
                        slug=t["slug"],
                        url=t["url"],
                        count=t.get("count", 0),
                    )
                )
            for p in data.get("pages", []):
                await s.merge(
                    Page(
                        id=f"{manga.id}_{p['number']}",
                        manga_id=manga.id,
                        number=p["number"],
                        url=p["path"],
                    )
                )
            await s.flush()
            await s.execute(delete(manga_tag).where(manga_tag.c.manga_id == manga.id))
            tag_rows = data.get("tags", [])
            if tag_rows:
                await s.execute(
                    insert(manga_tag),
                    [
                        {
                            "manga_id": manga.id,
                            "manga_title": manga.title,
                            "tag_id": t["id"],
                            "tag_type": t["type"],
                            "tag_slug": t["slug"],
                        }
                        for t in tag_rows
                    ],
                )
            # return {
            #     **model_to_dict(manga),
            #     "tags": [model_to_dict(t) for t in tags],
            # }
            return model_to_dict(manga)

    return await _run_with_session(_run, session)


def print_update(label: str, fields: dict[str, Any], lvl: int = 2) -> None:
    if DEBUG < lvl:
        return
    printc(f"Updating: {label} ..", "black", "bright_green")
    debug(fields, "Data to update", lvl=lvl)


async def update_manga(
    data: dict[str, Any], session: AsyncSession | None = None
) -> dict[str, Any]:
    manga_id = data["id"]
    fields = {k: v for k, v in data.items() if k != "id"}
    print_update(f"Manga [{manga_id}]", fields)

    async def _run(s: AsyncSession) -> dict[str, Any]:
        async with s.begin():
            await s.execute(update(Manga).where(Manga.id == manga_id).values(**fields))
            row = await s.get(Manga, manga_id)
            return model_to_dict(row) if row is not None else {}

    return await _run_with_session(_run, session)
