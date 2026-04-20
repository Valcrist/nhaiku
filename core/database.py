import re
from typing import Any, Literal
from collections.abc import Callable, Coroutine
from sqlalchemy import (
    delete,
    insert,
    update,
    select,
    or_,
    and_,
    func,
    exists,
    asc,
    desc,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from db.common import Base
from db.model.manga import Manga, Page, Tag
from db.relationships.manga import manga_tag
from db.schema.manga import MangaResponse, MangaUpdate, PageUpdate
from db.session import AsyncSessionLocal
from core.api_schema import GalleryListItem, GalleryPage
from toolbox.utils import DEBUG, printc, debug, warn


type _Runner[T] = Callable[[AsyncSession], Coroutine[Any, Any, T]]

LocalSearchSort = Literal["title", "date", "pages", "votes"]

_TYPED_SLUG_RE = re.compile(r'^(\w+):"([^"]+)"$')


def model_to_dict(obj: Base) -> dict[str, Any]:
    return {col.name: getattr(obj, col.name) for col in obj.__table__.columns}


def print_op(
    op: str, label: str, fields: dict[str, Any] | list[Any], lvl: int = 3
) -> None:
    if DEBUG < lvl:
        return
    printc(f"{op}: {label} ..", "bright_cyan", "blue")
    debug(fields, f"{label} {op.lower()}", lvl=lvl)


async def _run_with_session[T](fn: _Runner[T], session: AsyncSession | None) -> T:
    if session is not None:
        return await fn(session)
    async with AsyncSessionLocal() as s:
        async with s.begin():
            return await fn(s)


async def fetch_one(stmt: Any, session: AsyncSession | None = None) -> dict[str, Any]:
    async def _run(s: AsyncSession) -> dict[str, Any]:
        result = await s.execute(stmt)
        row = result.scalar_one_or_none()
        return model_to_dict(row) if row is not None else {}

    return await _run_with_session(_run, session)


async def fetch_art(id: int, session: AsyncSession | None = None) -> dict[str, Any]:
    async def _run(s: AsyncSession) -> dict[str, Any]:
        result = await s.execute(
            select(Manga.cover_file, Manga.thumbnail_file).where(Manga.id == id)
        )
        row = result.one_or_none()
        if row is None:
            return {}
        return {"cover_file": row.cover_file, "thumbnail_file": row.thumbnail_file}

    return await _run_with_session(_run, session)


async def query_manga(id: int, session: AsyncSession | None = None) -> dict[str, Any]:
    async def _run(s: AsyncSession) -> dict[str, Any]:
        result = await s.execute(
            select(Manga)
            .where(Manga.id == id)
            .options(selectinload(Manga.tags), selectinload(Manga.page_list))
        )
        manga = result.scalar_one_or_none()
        if manga is None:
            return {}
        return MangaResponse.model_validate(manga).model_dump()

    return await _run_with_session(_run, session)


async def save_manga(
    data: dict[str, Any], session: AsyncSession | None = None
) -> dict[str, Any]:
    async def _run(s: AsyncSession) -> dict[str, Any]:
        print_op("Save", f"[{data['id']}] {data['title']['pretty']}", data)
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
        return model_to_dict(manga)

    return await _run_with_session(_run, session)


async def update_manga(
    manga_id: int, data: dict[str, Any], session: AsyncSession | None = None
) -> dict[str, Any]:
    async def _run(s: AsyncSession) -> dict[str, Any]:
        id = int(manga_id)
        fields = MangaUpdate(**data).model_dump(exclude_none=True)
        if not fields:
            warn(f"No fields to update for Manga [{id}]")
            row = await s.get(Manga, id)
            return model_to_dict(row) if row is not None else {}
        print_op("Update", f"Manga [{id}]", fields)
        await s.execute(update(Manga).where(Manga.id == id).values(**fields))
        row = await s.get(Manga, id)
        return model_to_dict(row) if row is not None else {}

    return await _run_with_session(_run, session)


async def update_page(
    page_id: str, data: dict[str, Any], session: AsyncSession | None = None
) -> dict[str, Any]:
    async def _run(s: AsyncSession) -> dict[str, Any]:
        id = str(page_id)
        fields = PageUpdate(**data).model_dump(exclude_none=True)
        if not fields:
            warn(f"No fields to update for Page [{id}]")
            row = await s.get(Page, id)
            return model_to_dict(row) if row is not None else {}
        print_op("Update", f"Page [{id}]", fields)
        await s.execute(update(Page).where(Page.id == id).values(**fields))
        row = await s.get(Page, id)
        return model_to_dict(row) if row is not None else {}

    return await _run_with_session(_run, session)


async def get_missing_pages(
    manga_id: int, session: AsyncSession | None = None
) -> list[dict[str, Any]]:
    async def _run(s: AsyncSession) -> list[dict[str, Any]]:
        result = await s.execute(
            select(Page).where(
                Page.manga_id == manga_id,
                or_(Page.page_file == None, Page.page_file == ""),
            )
        )
        return [model_to_dict(row) for row in result.scalars().all()]

    return await _run_with_session(_run, session)


def _parse_term(term: str) -> tuple[bool, Any]:
    negated = term.startswith("-")
    bare = term.lstrip("-")

    m = _TYPED_SLUG_RE.match(bare)
    if m:
        tag_type, tag_slug = m.group(1), m.group(2)
        return negated, exists(
            select(manga_tag.c.manga_id).where(
                and_(
                    manga_tag.c.manga_id == Manga.id,
                    manga_tag.c.tag_type == tag_type,
                    manga_tag.c.tag_slug == tag_slug,
                )
            )
        )

    if "-" in bare and " " not in bare:
        return negated, exists(
            select(manga_tag.c.manga_id).where(
                and_(
                    manga_tag.c.manga_id == Manga.id,
                    manga_tag.c.tag_slug == bare,
                )
            )
        )

    tag_name_cond = exists(
        select(manga_tag.c.manga_id).where(
            and_(
                manga_tag.c.manga_id == Manga.id,
                manga_tag.c.tag_id == Tag.id,
                Tag.name.ilike(f"%{bare}%"),
            )
        )
    )
    return negated, or_(Manga.title_full.ilike(f"%{bare}%"), tag_name_cond)


async def search_manga(
    query: list[str],
    sort: LocalSearchSort,
    page: int,
    per_page: int,
    session: AsyncSession | None = None,
) -> GalleryPage:
    print_op("Search", "Manga", query, lvl=2)

    async def _run(s: AsyncSession) -> GalleryPage:
        filters: list[Any] = [Manga.nuked == False]
        for raw in query:
            stripped = raw.strip()
            if not stripped:
                continue
            negated, cond = _parse_term(stripped)
            filters.append(~cond if negated else cond)

        where_clause = and_(*filters)

        total: int = (
            await s.execute(select(func.count()).select_from(Manga).where(where_clause))
        ).scalar_one()

        if sort == "title":
            order_by = [asc(Manga.title_full)]
        elif sort == "date":
            order_by = [desc(Manga.created_at)]
        elif sort == "pages":
            order_by = [desc(Manga.pages), asc(Manga.title_full)]
        else:  # votes
            order_by = [desc(Manga.votes), asc(Manga.title_full)]

        rows = (
            (
                await s.execute(
                    select(Manga)
                    .where(where_clause)
                    .order_by(*order_by)
                    .limit(per_page)
                    .offset((page - 1) * per_page)
                )
            )
            .scalars()
            .all()
        )

        items = [
            GalleryListItem(
                id=m.id,
                media_id=m.media_id,
                english_title=m.title_full,
                japanese_title=m.title_jp,
                thumbnail=m.thumbnail_file or m.thumbnail or "",
                num_pages=m.pages,
            )
            for m in rows
        ]

        return GalleryPage(
            curr_page=page,
            num_pages=(total + per_page - 1) // per_page if per_page else 0,
            result=items,
            per_page=per_page,
            total=total,
        )

    return await _run_with_session(_run, session)
