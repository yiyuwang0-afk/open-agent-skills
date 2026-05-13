#!/usr/bin/env python3
"""Create sidebar-visible Obsidian topic pages from open content topics."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


DEFAULT_SCAN_FOLDERS = ("00_Inbox", "06_Sources", "01_Notes", "02_Claims", "03_Actions", "04_Outputs", "07_Projects")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sync Obsidian content-topic hub pages.")
    parser.add_argument("--vault", required=True, help="Obsidian vault root.")
    parser.add_argument("--topics-folder", default="05_Topic_Hubs/Content", help="Topic page folder relative to the vault.")
    parser.add_argument("--scan-folders", default=",".join(DEFAULT_SCAN_FOLDERS), help="Comma-separated folders to scan.")
    parser.add_argument("--field", default="topics", help="Open content topic field.")
    parser.add_argument("--dry-run", action="store_true", help="Print pages that would be created.")
    args = parser.parse_args(argv)

    vault = Path(args.vault).expanduser().resolve()
    scan_folders = tuple(item.strip() for item in args.scan_folders.split(",") if item.strip())
    created = sync_topic_pages(
        vault,
        topics_folder=args.topics_folder,
        scan_folders=scan_folders,
        field=args.field,
        dry_run=args.dry_run,
    )
    if not created:
        print("Topic pages are up to date.")
        return 0
    action = "would create" if args.dry_run else "created"
    for path in created:
        print(f"{action}: {path}")
    return 0


def sync_topic_pages(
    vault: Path,
    *,
    topics_folder: str,
    scan_folders: tuple[str, ...],
    field: str,
    dry_run: bool,
) -> list[Path]:
    target_dir = vault / topics_folder
    created: list[Path] = []
    for topic in sorted(collect_topics(vault, scan_folders=scan_folders, field=field)):
        target = target_dir / f"{topic}.md"
        if target.exists():
            continue
        created.append(target)
        if dry_run:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_topic_page(topic, field=field), encoding="utf-8")
    return created


def collect_topics(vault: Path, *, scan_folders: tuple[str, ...], field: str) -> set[str]:
    topics: set[str] = set()
    for folder in scan_folders:
        root = vault / folder
        if not root.exists():
            continue
        for note in root.rglob("*.md"):
            if note.name == ".gitkeep":
                continue
            topics.update(read_frontmatter_lists(note).get(field, []))
    return {topic for topic in topics if valid_topic_name(topic)}


def render_topic_page(topic: str, *, field: str) -> str:
    return f"""---
type: content-topic
topics:
  - {topic}
status: active
---
# {topic}

## Related Notes

```dataview
TABLE source, type, topics, hub_topics, status
WHERE contains({field}, this.file.name)
SORT file.mtime DESC
```
"""


def read_frontmatter_lists(path: Path) -> dict[str, list[str]]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    result: dict[str, list[str]] = {}
    current: str | None = None
    for raw in text[4:end].splitlines():
        if raw.startswith("  - ") and current:
            result.setdefault(current, []).append(raw[4:].strip().strip('"'))
            continue
        current = None
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"')
        if value and value != "[]":
            result[key] = [value]
        else:
            current = key
            result.setdefault(key, [])
    return result


def valid_topic_name(topic: str) -> bool:
    if not topic or len(topic) > 80:
        return False
    return not bool(re.search(r'[\\/:*?"<>|#\n\r]', topic))


if __name__ == "__main__":
    raise SystemExit(main())

