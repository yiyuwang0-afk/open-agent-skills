#!/usr/bin/env python3
"""Classify Markdown notes for an Obsidian knowledge-flow vault.

This script is intentionally generic and safe to publish. It uses an
OpenAI-compatible chat-completions endpoint configured by environment
variables and writes frontmatter fields for open content topics and optional
long-term hub topics.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Config:
    api_key: str
    base_url: str
    model: str
    hub_topics: list[str]
    language: str


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Classify Obsidian Markdown notes.")
    parser.add_argument("--vault", required=True, help="Obsidian vault root.")
    parser.add_argument("--folder", default="00_Inbox", help="Folder to scan, relative to vault.")
    parser.add_argument("--file", help="Classify one Markdown file.")
    parser.add_argument("--limit", type=int, help="Maximum notes to process.")
    parser.add_argument("--dry-run", action="store_true", help="Print output instead of writing files.")
    parser.add_argument("--hub-topics", default="", help="Comma-separated allowed long-term hub topics.")
    parser.add_argument("--language", default="en", choices=["en", "zh"], help="Frontmatter field language.")
    args = parser.parse_args(argv)

    vault = Path(args.vault).expanduser().resolve()
    load_env_file(vault / ".env")
    config = Config(
        api_key=os.environ.get("CLASSIFIER_API_KEY", ""),
        base_url=os.environ.get("CLASSIFIER_BASE_URL", "https://api.openai.com/v1"),
        model=os.environ.get("CLASSIFIER_MODEL", "gpt-4.1-mini"),
        hub_topics=[item.strip() for item in args.hub_topics.split(",") if item.strip()],
        language=args.language,
    )
    if not config.api_key:
        raise RuntimeError("CLASSIFIER_API_KEY is not set")

    notes = [Path(args.file).expanduser().resolve()] if args.file else iter_notes(vault / args.folder)
    if args.limit is not None:
        notes = notes[: args.limit]
    if not notes:
        print("No Markdown notes found.")
        return 0

    for note in notes:
        output = classify_note(note, config)
        if args.dry_run:
            print(f"--- {note} ---")
            print(output)
        else:
            write_with_frontmatter(note, output)
            print(f"classified: {note}")
    return 0


def iter_notes(folder: Path) -> list[Path]:
    if not folder.exists():
        return []
    return sorted(path for path in folder.rglob("*.md") if path.name != ".gitkeep")


def classify_note(path: Path, config: Config) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    prompt = build_prompt(text, config)
    payload = {
        "model": config.model,
        "messages": [
            {"role": "system", "content": "Return only a JSON object. Do not include explanations."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }
    request = urllib.request.Request(
        config.base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {config.api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Classifier API HTTP {exc.code}: {body}") from exc
    content = data["choices"][0]["message"]["content"]
    result = json.loads(content)
    return normalize_result(result, config)


def build_prompt(note_text: str, config: Config) -> str:
    if config.language == "zh":
        return f"""请为这篇 Obsidian Markdown 笔记生成 frontmatter 分类。

字段：
- 主题：开放内容主题，描述文章自身，例如 AI、商业、社会、媒体、消费、职业等。
- 长期主题：只能从用户配置的长期主题中选择；如果不适合，输出空数组。
- 摘要：一句话摘要。
- 核心判断：文章或笔记最有价值的判断。
- 使用场景：这条内容可以如何被使用。

可选长期主题：{config.hub_topics}

只输出 JSON object，键名使用中文：主题, 长期主题, 摘要, 核心判断, 使用场景, 置信度。

笔记：
{note_text[:30000]}
"""
    return f"""Classify this Obsidian Markdown note.

Fields:
- topics: open content topics about the note itself, such as AI, business, society, media, consumer, career.
- hub_topics: choose only from the configured long-term hubs; use [] if none fit.
- summary: one-sentence summary.
- key_claims: the note's most valuable claims.
- use_cases: how this note can be used later.

Allowed hub_topics: {config.hub_topics}

Return only a JSON object with keys: topics, hub_topics, summary, key_claims, use_cases, confidence.

Note:
{note_text[:30000]}
"""


def normalize_result(result: dict[str, Any], config: Config) -> dict[str, Any]:
    if config.language == "zh":
        allowed = set(config.hub_topics)
        long_term = [item for item in list_value(result.get("长期主题")) if item in allowed]
        return {
            "主题": list_value(result.get("主题")),
            "长期主题": long_term,
            "摘要": str(result.get("摘要") or ""),
            "核心判断": list_value(result.get("核心判断")),
            "使用场景": list_value(result.get("使用场景")),
            "置信度": float(result.get("置信度") or 0.0),
            "更新时间": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        }
    allowed = set(config.hub_topics)
    hub_topics = [item for item in list_value(result.get("hub_topics")) if item in allowed]
    return {
        "topics": list_value(result.get("topics")),
        "hub_topics": hub_topics,
        "summary": str(result.get("summary") or ""),
        "key_claims": list_value(result.get("key_claims")),
        "use_cases": list_value(result.get("use_cases")),
        "confidence": float(result.get("confidence") or 0.0),
        "updated": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
    }


def list_value(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def write_with_frontmatter(path: Path, metadata: dict[str, Any]) -> None:
    text = path.read_text(encoding="utf-8")
    _, body = split_frontmatter(text)
    path.write_text(render_frontmatter(metadata) + body.lstrip(), encoding="utf-8")


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end == -1:
        return "", text
    return text[4:end], text[end + 5 :]


def render_frontmatter(metadata: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in metadata.items():
        lines.extend(yaml_lines(key, value))
    lines.extend(["---", ""])
    return "\n".join(lines)


def yaml_lines(key: str, value: Any) -> list[str]:
    if isinstance(value, list):
        if not value:
            return [f"{key}: []"]
        lines = [f"{key}:"]
        for item in value:
            lines.append(f"  - {yaml_scalar(item)}")
        return lines
    return [f"{key}: {yaml_scalar(value)}"]


def yaml_scalar(value: Any) -> str:
    text = str(value).replace("\n", " ").strip()
    if not text:
        return ""
    if re.search(r"[:#\\[\\]{}&,*>!|%@`'\"]|^[-?]|\\s$", text):
        return json.dumps(text, ensure_ascii=False)
    return text


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


if __name__ == "__main__":
    raise SystemExit(main())

