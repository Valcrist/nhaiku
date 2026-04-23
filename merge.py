import asyncio
import argparse
from db.common import init_db
from core.merge import run_merge


async def main(threshold: int, match_pct: float) -> None:
    await init_db()
    await run_merge(threshold=threshold, match_pct=match_pct)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge duplicate manga entries")
    parser.add_argument(
        "--threshold",
        type=int,
        default=5,
        help="Minimum shared pages to consider a match (default: 5)",
    )
    parser.add_argument(
        "--match-pct",
        type=float,
        default=0.8,
        help="Min percentage of pages that must match master to merge (default: 0.8)",
    )
    args = parser.parse_args()
    asyncio.run(main(args.threshold, args.match_pct))
