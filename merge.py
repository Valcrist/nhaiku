import asyncio
import argparse
from db.common import init_db
from core.merge import run_merge


async def main(
    merge_threshold: int, merge_pct: float, relationship_threshold: int
) -> None:
    await init_db()
    await run_merge(
        merge_threshold=merge_threshold,
        merge_pct=merge_pct,
        relationship_threshold=relationship_threshold,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge duplicate manga entries")
    parser.add_argument(
        "--merge-threshold",
        type=int,
        default=8,
        help="Minimum shared pages required to merge into master (default: 8)",
    )
    parser.add_argument(
        "--merge-pct",
        type=float,
        default=0.8,
        help="Min percentage of pages that must match master to merge (default: 0.8)",
    )
    parser.add_argument(
        "--relationship-threshold",
        type=int,
        default=5,
        help="Minimum shared pages to consider manga related (default: 5)",
    )
    args = parser.parse_args()
    asyncio.run(main(args.merge_threshold, args.merge_pct, args.relationship_threshold))
