#!/usr/bin/env python3
"""Create sidebar-visible Obsidian topic pages from coarse topic fields."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


DEFAULT_SCAN_FOLDERS = ("00_Inbox", "06_Sources")
GENERATED_START = "<!-- AUTO-GENERATED:START -->"
GENERATED_END = "<!-- AUTO-GENERATED:END -->"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sync Obsidian content-topic hub pages.")
    parser.add_argument("--vault", required=True, help="Obsidian vault root.")
    parser.add_argument("--topics-folder", default="05_Topic_Hubs/Content", help="Topic page folder relative to the vault.")
    parser.add_argument("--scan-folders", default=",".join(DEFAULT_SCAN_FOLDERS), help="Comma-separated folders to scan.")
    parser.add_argument("--domain-field", default="domains", help="Top-level topic field.")
    parser.add_argument("--subtopic-field", default="subtopics", help="Second-level topic field.")
    parser.add_argument("--dry-run", action="store_true", help="Print pages that would be created.")
    args = parser.parse_args(argv)

    vault = Path(args.vault).expanduser().resolve()
    scan_folders = tuple(item.strip() for item in args.scan_folders.split(",") if item.strip())
    created = sync_topic_pages(
        vault,
        topics_folder=args.topics_folder,
        scan_folders=scan_folders,
        domain_field=args.domain_field,
        subtopic_field=args.subtopic_field,
        dry_run=args.dry_run,
    )
    if not created:
        print("Topic pages are up to date.")
        return 0
    action = "would create" if args.dry_run else "created"
    for path in created:
        print(f"{action}: {display_path(path, vault)}")
    return 0


def sync_topic_pages(
    vault: Path,
    *,
    topics_folder: str,
    scan_folders: tuple[str, ...],
    domain_field: str,
    subtopic_field: str,
    dry_run: bool,
) -> list[Path]:
    target_dir = vault / topics_folder
    created: list[Path] = []
    for domain, subtopics in sorted(collect_topic_tree(vault, scan_folders=scan_folders, domain_field=domain_field, subtopic_field=subtopic_field).items()):
        domain_dir = target_dir / domain
        domain_page = domain_dir / f"{domain}.md"
        if not domain_page.exists():
            created.append(domain_page)
            if not dry_run:
                domain_page.parent.mkdir(parents=True, exist_ok=True)
                domain_page.write_text(
                    upsert_generated_block(
                        render_domain_page(domain, domain_field=domain_field),
                        render_generated_links([]),
                    ),
                    encoding="utf-8",
                )
        elif not dry_run:
            maybe_update_existing_page(domain_page, render_generated_links([]))
        for subtopic in sorted(subtopics):
            subtopic_page = domain_dir / f"{subtopic}.md"
            if subtopic_page.exists():
                if not dry_run:
                    maybe_update_existing_page(subtopic_page, render_generated_links([]))
                continue
            created.append(subtopic_page)
            if not dry_run:
                subtopic_page.parent.mkdir(parents=True, exist_ok=True)
                subtopic_page.write_text(
                    upsert_generated_block(
                        render_subtopic_page(domain, subtopic, domain_field=domain_field, subtopic_field=subtopic_field),
                        render_generated_links([]),
                    ),
                    encoding="utf-8",
                )
    return created


def collect_topic_tree(vault: Path, *, scan_folders: tuple[str, ...], domain_field: str, subtopic_field: str) -> dict[str, set[str]]:
    tree: dict[str, set[str]] = {}
    for folder in scan_folders:
        root = vault / folder
        if not root.exists():
            continue
        for note in root.rglob("*.md"):
            if note.name == ".gitkeep":
                continue
            metadata = read_frontmatter_lists(note)
            domains = [item for item in metadata.get(domain_field, []) if valid_topic_name(item)]
            subtopics = [item for item in metadata.get(subtopic_field, []) if valid_topic_name(item)]
            for domain in domains:
                tree.setdefault(domain, set()).update(subtopics)
    return tree


def render_domain_page(domain: str, *, domain_field: str) -> str:
    return f"""---
type: content-domain
{domain_field}:
  - {domain}
status: active
---
# {domain}

## Generated Links

## Related Notes

```dataview
TABLE source, type, topics, hub_topics, status
WHERE contains({domain_field}, this.file.name)
SORT file.mtime DESC
```
"""


def render_subtopic_page(domain: str, subtopic: str, *, domain_field: str, subtopic_field: str) -> str:
    return f"""---
type: content-subtopic
{domain_field}:
  - {domain}
{subtopic_field}:
  - {subtopic}
status: active
---
# {subtopic}

## Generated Links

## Related Notes

```dataview
TABLE source, type, topics, hub_topics, status
WHERE contains({domain_field}, "{domain}") AND contains({subtopic_field}, this.file.name)
SORT file.mtime DESC
```
"""


def maybe_update_existing_page(path: Path, generated_block: str) -> bool:
    original = path.read_text(encoding="utf-8")
    if GENERATED_START not in original or GENERATED_END not in original:
        print(f"skipped unmarked topic page: {path.name}")
        return False
    updated = upsert_generated_block(original, generated_block)
    if updated != original:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def display_path(path: Path, base: Path) -> str:
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return path.name


def upsert_generated_block(text: str, generated_block: str) -> str:
    block = f"{GENERATED_START}\n{generated_block.rstrip()}\n{GENERATED_END}"
    if GENERATED_START in text and GENERATED_END in text:
        start = text.index(GENERATED_START)
        end = text.index(GENERATED_END, start) + len(GENERATED_END)
        return text[:start] + block + text[end:]
    return text.rstrip() + "\n\n" + block + "\n"


def render_generated_links(links: list[str]) -> str:
    if not links:
        return "- Add curated links or generated backlinks here."
    return "\n".join(f"- {link}" for link in links)


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
