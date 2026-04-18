import sys
import asyncio
from core.exceptions import NHaikuError, NHaikuWarning
from core.api_client import get_galleries, get_gallery, get_related_galleries
from core.indexer import *
from toolbox.utils import DEBUG, debug, err, warn, hr, json2var


REINDEX = False
REINDEX = True

sys.stdout.reconfigure(line_buffering=True)

print(f"DEBUG type: {type(DEBUG)}")
print(f"DEBUG value: {DEBUG}")


async def manual_scrape():
    mangas = json2var("ref/mangas.json")
    for manga in mangas:
        id = manga.get("id") or 0
        votes = manga.get("votes", 0)
        pages = manga.get("num_pages", 0)
        if not id or not votes or pages > 3:
            continue
        debug(manga)
        print(f"Manga ID: {id}, Votes: {votes}, Pages: {pages}")
        manga = await get_manga(id, reindex=REINDEX)
        # debug(manga)

        break
    # gs = await get_galleries(page=2)
    # debug(gs)


if __name__ == "__main__":
    asyncio.run(manual_scrape())
