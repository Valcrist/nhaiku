import asyncio
from core.indexer import proc_manga
from core.database import update_manga
from toolbox.utils import debug, warn, json2var, printc


REINDEX = True


async def backfill():
    mangas = json2var("ref/mangas.json")
    for manga in mangas:
        try:
            id = int(manga.get("id") or 0)
            title = manga.get("title", "")
            votes = manga.get("votes", 0)
            if not id or not votes:
                continue
            manga = await proc_manga(id, reindex=REINDEX)
            await update_manga(id, {"votes": votes})
            printc(f"Completed backfill for manga: [{id}] {title}", "bright_magenta")
        except Exception as e:
            warn(f"Error backfilling manga: {manga}\n\n{e}")


if __name__ == "__main__":
    asyncio.run(backfill())
