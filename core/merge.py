from collections import defaultdict, deque
from typing import Any
from sqlalchemy import and_, or_, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from db.model.manga import Manga, Page
from db.relationships.manga import manga_tag
from db.session import AsyncSessionLocal
from toolbox.utils import printc, warn


async def run_merge(threshold: int = 5) -> None:
    async with AsyncSessionLocal() as s:
        async with s.begin():
            await _run_merge(s, threshold)


async def _run_merge(s: AsyncSession, threshold: int) -> None:
    printc("Loading pages from database...", "cyan")
    rows = (
        await s.execute(
            select(Page.manga_id, Page.page_file).where(Page.page_file.isnot(None))
        )
    ).all()

    page_sets: dict[int, set[str]] = defaultdict(set)
    for manga_id, page_file in rows:
        page_sets[manga_id].add(page_file)

    manga_ids = list(page_sets.keys())
    if not manga_ids:
        printc("No downloaded pages found — nothing to merge", "yellow")
        return

    printc(f"Loaded {len(rows)} pages across {len(manga_ids)} manga", "cyan")

    printc("Building similarity graph...", "cyan")
    pf_to_manga: dict[str, list[int]] = defaultdict(list)
    for manga_id, page_file in rows:
        pf_to_manga[page_file].append(manga_id)

    shared_counts: dict[tuple[int, int], int] = defaultdict(int)
    for mids in pf_to_manga.values():
        if len(mids) < 2:
            continue
        for i, a in enumerate(mids):
            for b in mids[i + 1 :]:
                shared_counts[(min(a, b), max(a, b))] += 1

    adj: dict[int, set[int]] = defaultdict(set)
    for (a, b), count in shared_counts.items():
        if count >= threshold:
            adj[a].add(b)
            adj[b].add(a)

    printc(
        f"Found {len(adj)} manga with at least one match (threshold={threshold})",
        "cyan",
    )

    printc("Finding connected components...", "cyan")
    components: list[set[int]] = []
    visited: set[int] = set()
    for start in manga_ids:
        if start in visited:
            continue
        component: set[int] = set()
        queue: deque[int] = deque([start])
        while queue:
            node = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            component.add(node)
            queue.extend(adj[node] - visited)
        components.append(component)

    multi = [c for c in components if len(c) > 1]
    printc(
        f"Found {len(multi)} merge group(s) across {sum(len(c) for c in multi)} manga",
        "bright_cyan",
    )

    # Load existing related values for all manga in multi-components
    all_ids = [mid for c in multi for mid in c]
    existing_related: dict[int, int | None] = {}
    if all_ids:
        related_rows = (
            await s.execute(
                select(Manga.id, Manga.related).where(Manga.id.in_(all_ids))
            )
        ).all()
        existing_related = {r.id: r.related for r in related_rows}

    for i, component in enumerate(multi, 1):
        printc(f"Processing group {i}/{len(multi)} ({len(component)} manga)...", "cyan")
        await _process_component(s, component, page_sets, existing_related, threshold)

    # Clear merged/related for manga no longer in any qualifying component
    multi_ids = {mid for c in multi for mid in c}
    stale_filter = or_(Manga.merged.isnot(None), Manga.related.isnot(None))
    if multi_ids:
        stale_filter = and_(stale_filter, ~Manga.id.in_(multi_ids))
    cleared = await s.execute(
        update(Manga).where(stale_filter).values(merged=None, related=None)
    )
    if cleared.rowcount:
        printc(f"Cleared {cleared.rowcount} stale merged/related record(s)", "yellow")

    printc("Done.", "bright_cyan")


async def _process_component(
    s: AsyncSession,
    component: set[int],
    page_sets: dict[int, set[str]],
    existing_related: dict[int, int | None],
    threshold: int,
) -> None:
    ids = list(component)

    # Master = manga with most downloaded pages; tie-break by min id
    master_id = min(ids, key=lambda mid: (-len(page_sets[mid]), mid))
    master_pages = page_sets[master_id]

    # Determine which manga merge into master
    merged_ids: list[int] = []
    non_merged_ids: list[int] = []
    for mid in ids:
        if mid == master_id:
            continue
        shared = page_sets[mid] & master_pages
        if page_sets[mid] <= master_pages and len(shared) >= threshold:
            merged_ids.append(mid)
        else:
            non_merged_ids.append(mid)

    # Assign related group id — stable: reuse any existing value, else min(non-merged)
    non_merged_members = [master_id] + non_merged_ids
    existing = [
        existing_related.get(mid)
        for mid in non_merged_members
        if existing_related.get(mid) is not None
    ]
    group_id = min(existing) if existing else min(non_merged_members)

    printc(
        f"  Group {group_id}: master={master_id} merge={merged_ids} related={non_merged_ids}",
        "bright_green",
    )

    # Update merged records: merged=master_id, related=NULL
    if merged_ids:
        await s.execute(
            update(Manga)
            .where(Manga.id.in_(merged_ids))
            .values(merged=master_id, related=None)
        )

    # Update non-merged (master + others): merged=NULL, related=group_id
    if non_merged_members:
        await s.execute(
            update(Manga)
            .where(Manga.id.in_(non_merged_members))
            .values(merged=None, related=group_id)
        )

    # Merge tags from merged manga into master
    if merged_ids:
        await _merge_tags(s, master_id, merged_ids)


async def _merge_tags(s: AsyncSession, master_id: int, merged_ids: list[int]) -> None:
    # Load master manga title for denormalization
    master = await s.get(Manga, master_id)
    if master is None:
        warn(f"Master manga {master_id} not found during tag merge")
        return

    # Load all tag rows from merged manga
    source_rows = (
        await s.execute(
            select(
                manga_tag.c.tag_id,
                manga_tag.c.tag_type,
                manga_tag.c.tag_slug,
            ).where(manga_tag.c.manga_id.in_(merged_ids))
        )
    ).all()

    if not source_rows:
        return

    # Deduplicate by tag_id
    seen: set[int] = set()
    to_insert: list[dict[str, Any]] = []
    for row in source_rows:
        if row.tag_id in seen:
            continue
        seen.add(row.tag_id)
        to_insert.append(
            {
                "manga_id": master_id,
                "manga_title": master.title,
                "tag_id": row.tag_id,
                "tag_type": row.tag_type,
                "tag_slug": row.tag_slug,
            }
        )

    if to_insert:
        await s.execute(pg_insert(manga_tag).values(to_insert).on_conflict_do_nothing())
