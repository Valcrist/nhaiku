from typing import Any
from sqlalchemy import delete, insert, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from helpers.database import fetch_one, model_to_dict
from db.model.manga import Manga, Tag
from db.relationships.manga import manga_tag
from db.session import AsyncSessionLocal
from helpers.api_client import get_gallery
from toolbox.utils import err, warn, debug


async def query_manga(id: int, session: AsyncSession | None = None) -> dict[str, Any]:
    return await fetch_one(select(Manga).where(Manga.id == id), session)


async def save_manga(data: dict[str, Any]) -> dict[str, Any]:
    async with AsyncSessionLocal() as session:
        try:
            async with session.begin():
                manga = await session.merge(
                    Manga(
                        id=data["id"],
                        media_id=data["media_id"],
                        title=data["title"]["pretty"],
                        title_full=data["title"]["english"],
                        title_jp=data["title"]["japanese"],
                        cover=data["cover"]["path"],
                        thumbnail=data["thumbnail"]["path"],
                        scanlator=data.get("scanlator", ""),
                        upload_date=data["upload_date"],
                        pages=data["num_pages"],
                        faves=data["num_favorites"],
                    )
                )
                for t in data.get("tags", []):
                    await session.merge(
                        Tag(
                            id=t["id"],
                            type=t["type"],
                            name=t["name"],
                            slug=t["slug"],
                            url=t["url"],
                            count=t["count"],
                        )
                    )
                await session.flush()
                await session.execute(
                    delete(manga_tag).where(manga_tag.c.manga_id == manga.id)
                )
                tag_rows = data.get("tags", [])
                if tag_rows:
                    await session.execute(
                        insert(manga_tag),
                        [
                            {
                                "manga_id": manga.id,
                                "manga_title": manga.title,
                                "tag_id": t["id"],
                                "tag_slug": t["slug"],
                            }
                            for t in tag_rows
                        ],
                    )
                return model_to_dict(manga)
        except SQLAlchemyError as e:
            err(f"Failed to save manga {data['id']}: {e}")
            return {}


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
            manga = await get_gallery(int(id))
        return manga
    except Exception as e:
        err(f"Failed to get manga {id}: {e}")
        return {}
