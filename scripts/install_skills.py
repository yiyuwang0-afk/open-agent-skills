#!/usr/bin/env python3
"""Install public Skills into a local agent skills directory.

The installer copies directories that contain SKILL.md. It is intentionally
simple and cross-platform: no shell-specific commands, no service setup, and no
credential handling.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKS = {
    "agent-workflow-skills": ROOT / "agent-workflow-skills" / "skills",
    "obsidian-knowledge-flow": ROOT,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Install public Skills.")
    parser.add_argument("--target", required=True, help="Destination skills directory.")
    parser.add_argument(
        "--pack",
        choices=["all", *PACKS.keys()],
        default="all",
        help="Skill pack to install.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would be copied.")
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    skills = discover_skills(args.pack)
    if not skills:
        raise SystemExit("No skills found to install.")

    if not args.dry_run:
        target.mkdir(parents=True, exist_ok=True)

    for skill in skills:
        destination = target / skill.name
        if args.dry_run:
            print(f"would install: {skill} -> {destination}")
            continue
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(skill, destination, ignore=ignore_private_files)
        print(f"installed: {skill.name} -> {destination}")

    return 0


def discover_skills(pack: str) -> list[Path]:
    roots = PACKS.values() if pack == "all" else [PACKS[pack]]
    skills: list[Path] = []
    for root in roots:
        if root.name == "obsidian-knowledge-flow" and (root / "SKILL.md").exists():
            skills.append(root)
            continue
        for child in sorted(root.iterdir()):
            if child.is_dir() and (child / "SKILL.md").exists():
                skills.append(child)
    return skills


def ignore_private_files(_directory: str, names: list[str]) -> set[str]:
    ignored = {
        ".git",
        ".DS_Store",
        ".env",
        "__pycache__",
        ".pytest_cache",
    }
    ignored.update(name for name in names if name.endswith((".pyc", ".log", ".pid", ".sqlite", ".db")))
    return ignored.intersection(names)


if __name__ == "__main__":
    raise SystemExit(main())
