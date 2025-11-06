"""Import Markdown posts into the MAI database.

Usage:
    python scripts/import_markdown.py --dir ./content

The script will scan all ``.md`` files inside the target directory, derive a
slug from each filename, and create a new post if the slug does not already
exist in the database. Existing posts (matched by slug) will be skipped.
"""

from __future__ import annotations

import argparse
import asyncio
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import crud, schemas
from app.database import AsyncSessionFactory, engine

DEFAULT_CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"


@dataclass
class ParsedPost:
    slug: str
    title: str
    excerpt: str
    source_path: Path


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name).strip("-")
    return slug.lower() or "post"


def extract_excerpt(markdown_body: str) -> str:
    # Pick the first non-empty paragraph as excerpt, strip simple markdown syntax
    paragraphs = [paragraph.strip() for paragraph in markdown_body.split("\n\n")]
    for paragraph in paragraphs:
        if not paragraph:
            continue
        # strip link syntax [text](url) -> text
        paragraph = re.sub(r"\[(?P<text>[^\]]+)\]\([^\)]+\)", r"\g<text>", paragraph)
        # remove residual markdown symbols such as #, *, `, >, _
        paragraph = re.sub(r"[#>*`_]", "", paragraph)
        return paragraph[:180] + ("..." if len(paragraph) > 180 else "")
    return ""


def parse_markdown_file(path: Path) -> ParsedPost:
    raw_text = path.read_text(encoding="utf-8")
    lines = raw_text.splitlines()

    title = path.stem.replace("_", " ").strip()
    body_start = 0

    for idx, line in enumerate(lines):
        if line.startswith("# "):
            title = line.lstrip("# ").strip()
            body_start = idx + 1
            break

    markdown_body = "\n".join(lines[body_start:]).strip()
    if not markdown_body:
        markdown_body = raw_text.strip()

    excerpt = extract_excerpt(markdown_body)

    return ParsedPost(
        slug=slugify(path.stem),
        title=title or path.stem,
        excerpt=excerpt,
        source_path=path,
    )


async def import_markdown(directory: Path) -> tuple[int, int]:
    created = 0
    skipped = 0

    target_dir = DEFAULT_CONTENT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    async with AsyncSessionFactory() as session:
        for md_file in sorted(directory.glob("*.md")):
            parsed = parse_markdown_file(md_file)
            existing = await crud.get_post_by_slug(session, parsed.slug)
            if existing:
                skipped += 1
                print(f"[skip] {md_file.name} -> slug '{parsed.slug}' already exists")
                continue

            destination = target_dir / f"{parsed.slug}{md_file.suffix}"
            try:
                if md_file.resolve() != destination.resolve():
                    shutil.copy2(parsed.source_path, destination)
            except FileNotFoundError:
                shutil.copy2(parsed.source_path, destination)

            payload = schemas.PostCreate(
                title=parsed.title,
                excerpt=parsed.excerpt or None,
                content_path=f"/content/{destination.name}",
                tags=[],
                slug=parsed.slug,
            )
            await crud.create_post(session, payload)
            created += 1
            print(f"[add]  {md_file.name} -> created post '{parsed.title}'")

    return created, skipped


def validate_directory(path: Path) -> Path:
    if not path.exists() or not path.is_dir():
        raise FileNotFoundError(f"目录 {path} 不存在或不是文件夹")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import markdown posts into the MAI blog")
    parser.add_argument(
        "--dir",
        dest="directory",
        type=lambda value: validate_directory(Path(value).expanduser().resolve()),
        default=DEFAULT_CONTENT_DIR,
        help=f"Markdown 文件所在目录 (默认: {DEFAULT_CONTENT_DIR})",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    created, skipped = await import_markdown(args.directory)
    print(f"完成：新增 {created} 篇，跳过 {skipped} 篇。")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
