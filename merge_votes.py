import asyncio
from sqlalchemy import select, update, func
from db.session import AsyncSessionLocal
from db.model.manga import Manga


async def main() -> None:
    async with AsyncSessionLocal() as s:
        # --- Related groups: all masters with same related value ---
        result = await s.execute(
            select(Manga.related).where(Manga.related.isnot(None)).distinct()
        )
        group_ids = [r[0] for r in result.all()]

        for group_id in group_ids:
            result = await s.execute(
                select(Manga.id).where(
                    Manga.related == group_id, Manga.merged.is_(None)
                )
            )
            master_ids = [r[0] for r in result.all()]

            result = await s.execute(
                select(Manga.id).where(Manga.merged.in_(master_ids))
            )
            merged_ids = [r[0] for r in result.all()]

            all_ids = master_ids + merged_ids
            result = await s.execute(
                select(func.max(Manga.votes)).where(Manga.id.in_(all_ids))
            )
            max_votes = result.scalar_one_or_none() or 0

            await s.execute(
                update(Manga).where(Manga.id.in_(all_ids)).values(votes=max_votes)
            )
            print(
                f"related group {group_id}: {len(all_ids)} mangas → {max_votes} votes"
            )

        # --- Standalone merged groups: masters with no related but have merged children ---
        result = await s.execute(
            select(Manga.id).where(Manga.merged.is_(None), Manga.related.is_(None))
        )
        standalone_ids = [r[0] for r in result.all()]

        for master_id in standalone_ids:
            result = await s.execute(select(Manga.id).where(Manga.merged == master_id))
            merged_ids = [r[0] for r in result.all()]
            if not merged_ids:
                continue

            all_ids = [master_id] + merged_ids
            result = await s.execute(
                select(func.max(Manga.votes)).where(Manga.id.in_(all_ids))
            )
            max_votes = result.scalar_one_or_none() or 0

            await s.execute(
                update(Manga).where(Manga.id.in_(all_ids)).values(votes=max_votes)
            )
            print(f"master {master_id}: {len(all_ids)} mangas → {max_votes} votes")

        await s.commit()
        print("Done.")


asyncio.run(main())
