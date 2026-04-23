import asyncio
import argparse
from db.common import init_db
from core.merge import run_merge


async def main(threshold: int) -> None:
    await init_db()
    await run_merge(threshold=threshold)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge duplicate manga entries")
    parser.add_argument(
        "--threshold",
        type=int,
        default=5,
        help="Minimum shared pages to consider a match (default: 5)",
    )
    args = parser.parse_args()
    asyncio.run(main(args.threshold))
