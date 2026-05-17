#!/usr/bin/env python3
"""Lightweight privacy scan for the public Skills repository."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


DEFAULT_PATTERNS = [
    r"/Users/[A-Za-z0-9._-]+",
    r"C:\\Users\\[^\\\s]+",
    r"ObsidianVaults",
    r"\.openclaw",
    r"FEISHU_APP_SECRET\s*=\s*\S+",
    r"CLASSIFIER_API_KEY\s*=\s*\S+",
    r"DEEPSEEK_API_KEY\s*=\s*\S+",
    r"sk-[A-Za-z0-9]{20,}",
    r"\bou_[A-Za-z0-9]{8,}\b",
    r"\boc_[A-Za-z0-9]{8,}\b",
    r"\bom_[A-Za-z0-9]{8,}\b",
]

TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".py",
    ".js",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ps1",
    ".sh",
    ".example",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan for private paths and credentials.")
    parser.add_argument("path", nargs="?", default=".", help="Repository path to scan.")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    regexes = [re.compile(pattern) for pattern in DEFAULT_PATTERNS]
    findings: list[tuple[Path, int, str]] = []

    for path in iter_text_files(root):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(lines, start=1):
            if any(regex.search(line) for regex in regexes):
                findings.append((path, number, line.strip()[:180]))

    if findings:
        for path, number, line in findings:
            print(f"{path.relative_to(root)}:{number}: {line}")
        raise SystemExit(1)

    print("Privacy scan passed.")
    return 0


def iter_text_files(root: Path):
    for path in root.rglob("*"):
        if any(part in {".git", "__pycache__", ".pytest_cache"} for part in path.parts):
            continue
        if path.name == "privacy_scan.py":
            continue
        if path.is_file() and path.suffix in TEXT_SUFFIXES:
            yield path


if __name__ == "__main__":
    raise SystemExit(main())
