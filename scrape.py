import asyncio
from helpers.exceptions import NHaikuError, NHaikuWarning
from helpers.api_client import get_galleries, get_gallery, get_related_galleries
from helpers.indexer import *
from toolbox.utils import debug, err, warn, hr, json2var


REINDEX = False
REINDEX = True


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
        debug(manga)

        break
    # gs = await get_galleries(page=2)
    # debug(gs)


if __name__ == "__main__":
    asyncio.run(manual_scrape())
