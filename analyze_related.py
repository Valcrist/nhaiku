import asyncio
from collections import defaultdict, deque
from sqlalchemy import select
from db.common import init_db
from db.model.manga import Page
from db.session import AsyncSessionLocal

TARGET_IDS = {
    588144,
    516556,
    501101,
    499937,
    492964,
    446134,
    411261,
    405652,
    346339,
    340030,
    317472,
    283725,
}

BLANK_PAGES = {
    "00/00/00/00/00000000.webp",
    "ff/ff/ff/ff/ffffffff.webp",
}

THRESHOLD = 8


async def main() -> None:
    await init_db()

    async with AsyncSessionLocal() as s:
        rows = (
            await s.execute(
                select(Page.manga_id, Page.page_file).where(
                    Page.page_file.isnot(None),
                    Page.page_file.notin_(BLANK_PAGES),
                )
            )
        ).all()

    print(f"Loaded {len(rows)} pages across all manga")

    page_sets: dict[int, set[str]] = defaultdict(set)
    for manga_id, page_file in rows:
        page_sets[manga_id].add(page_file)

    # Build adjacency graph over all manga
    pf_to_manga: dict[str, list[int]] = defaultdict(list)
    for manga_id, page_file in rows:
        pf_to_manga[page_file].append(manga_id)

    adj: dict[int, set[int]] = defaultdict(set)
    for mids in pf_to_manga.values():
        if len(mids) < 2:
            continue
        for i, a in enumerate(mids):
            for b in mids[i + 1 :]:
                # Only add edge once we know the full shared count
                pass

    shared_counts: dict[tuple[int, int], int] = defaultdict(int)
    for mids in pf_to_manga.values():
        if len(mids) < 2:
            continue
        for i, a in enumerate(mids):
            for b in mids[i + 1 :]:
                shared_counts[(min(a, b), max(a, b))] += 1

    for (a, b), count in shared_counts.items():
        if count >= THRESHOLD:
            adj[a].add(b)
            adj[b].add(a)

    # Find which component each target ID lands in
    visited: set[int] = set()
    components: list[set[int]] = []
    for start in page_sets:
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

    print("\nComponents containing target IDs:")
    for comp in components:
        overlap = comp & TARGET_IDS
        if not overlap:
            continue
        print(f"  Component size={len(comp)}, targets={sorted(overlap)}")
        if len(overlap) > 1:
            # Find shortest BFS path between first two targets in this component
            # to expose the bridge manga
            targets = sorted(overlap)
            for i in range(len(targets)):
                for j in range(i + 1, len(targets)):
                    src, dst = targets[i], targets[j]
                    path = _bfs_path(adj, src, dst)
                    if path and len(path) > 2:
                        bridge = [n for n in path if n not in TARGET_IDS]
                        if bridge:
                            print(f"    {src} -> {dst} via: {path}")
                            for node in bridge:
                                shared_with_prev = len(
                                    page_sets[node]
                                    & page_sets[path[path.index(node) - 1]]
                                )
                                shared_with_next = len(
                                    page_sets[node]
                                    & page_sets[path[path.index(node) + 1]]
                                )
                                print(
                                    f"      bridge {node}: {shared_with_prev} shared with {path[path.index(node)-1]}, {shared_with_next} shared with {path[path.index(node)+1]}"
                                )


def _bfs_path(adj: dict[int, set[int]], src: int, dst: int) -> list[int] | None:
    prev: dict[int, int] = {src: -1}
    queue: deque[int] = deque([src])
    while queue:
        node = queue.popleft()
        if node == dst:
            path = []
            cur = dst
            while cur != -1:
                path.append(cur)
                cur = prev[cur]
            return list(reversed(path))
        for nb in adj[node]:
            if nb not in prev:
                prev[nb] = node
                queue.append(nb)
    return None


if __name__ == "__main__":
    asyncio.run(main())
