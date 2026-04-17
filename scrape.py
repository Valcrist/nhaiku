import asyncio
from helpers.exceptions import NHaikuError, NHaikuWarning
from helpers.api_client import get_galleries, get_gallery, get_related_galleries
from helpers.manga import *
from toolbox.utils import debug, err, warn, hr, json2var


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
        hr()

        # manga = await get_gallery(id)
        # debug(manga)
        # hr()

        # related = await get_related_galleries(id)
        # debug(related)

        manga = await index_manga(id)
        debug(manga)
        hr()

        break
    # gs = await get_galleries(page=2)
    # debug(gs)


if __name__ == "__main__":
    asyncio.run(manual_scrape())
