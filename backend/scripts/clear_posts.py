"""Clean up posts from the MAI database.

Examples:
    # Delete every post (requires --yes to avoid accidental use)
    python scripts/clear_posts.py --all --yes

    # Delete specific posts by slug
    python scripts/clear_posts.py --slug calm-productivity-stack micro-interactions
"""

from __future__ import annotations

import argparse
import asyncio

from sqlalchemy import delete

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import crud, models
from app.database import AsyncSessionFactory, engine


async def delete_all() -> int:
    async with AsyncSessionFactory() as session:
        result = await session.execute(delete(models.Post))
        await session.commit()
        return result.rowcount or 0


async def delete_by_slugs(slugs: list[str]) -> None:
    async with AsyncSessionFactory() as session:
        for slug in slugs:
            post = await crud.get_post_by_slug(session, slug)
            if not post:
                print(f"[skip] 未找到 slug = {slug}")
                continue
            await crud.delete_post(session, post)
            print(f"[delete] 已移除 slug = {slug}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Delete posts from the MAI database")
    parser.add_argument("--all", action="store_true", help="删除所有文章")
    parser.add_argument(
        "--yes",
        action="store_true",
        help="确认执行危险操作 (删除全部文章时必须加 --yes)",
    )
    parser.add_argument(
        "--slug",
        nargs="+",
        help="按 slug 删除指定文章，可一次输入多个",
    )
    args = parser.parse_args()

    if args.all and args.slug:
        parser.error("--all 与 --slug 不能同时使用")

    if not args.all and not args.slug:
        parser.error("必须指定 --all 或 --slug")

    if args.all and not args.yes:
        parser.error("删除全部文章需要同时传入 --yes 以确认操作")

    return args


async def main() -> None:
    args = parse_args()
    if args.all:
        deleted = await delete_all()
        print(f"已删除所有文章，共 {deleted} 篇。")
    else:
        await delete_by_slugs(args.slug)
        print("指定的文章处理完成。")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
