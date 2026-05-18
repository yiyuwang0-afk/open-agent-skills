#!/usr/bin/env python3
"""Import WeChat public-account articles into an Obsidian inbox."""

from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


def is_wechat_url(url: str) -> bool:
    if not url:
        return False
    host = urlparse(url).netloc.lower()
    return host == "mp.weixin.qq.com" or host.endswith(".mp.weixin.qq.com")


def save_wechat_article(vault: Path, inbox: str, message: Any) -> Path:
    url = str(getattr(message, "source_url", "") or "").strip()
    if not is_wechat_url(url):
        raise ValueError(f"Not a WeChat public-account URL: {url}")

    article = parse_wechat_article(url)
    title = first_non_empty(
        article_value(article, "title"),
        title_from_text(str(getattr(message, "text", "") or "")),
        "WeChat article",
    )
    folder = vault / inbox
    folder.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    target = unique_path(folder / f"{timestamp}-{safe_filename(title)}.md")
    target.write_text(render_wechat_article(article, url, title), encoding="utf-8")
    return target


def parse_wechat_article(url: str) -> Any:
    try:
        from wechat_article_parser import parse
    except ImportError as exc:
        raise RuntimeError(
            "Install WeChat parser first: python -m pip install -r obsidian-knowledge-flow/requirements.txt"
        ) from exc
    return parse(url)


def render_wechat_article(article: Any, url: str, title: str) -> str:
    captured = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    author = first_non_empty(
        article_value(article, "author"),
        article_value(article, "account"),
        article_value(article, "nickname"),
    )
    published = first_non_empty(
        article_value(article, "published"),
        article_value(article, "publish_time"),
        article_value(article, "date"),
    )
    markdown = first_non_empty(
        article_value(article, "markdown"),
        article_value(article, "md"),
        article_value(article, "content"),
        article_value(article, "text"),
    )
    if not markdown:
        markdown = json.dumps(normalize_article(article), ensure_ascii=False, indent=2)

    return "\n".join(
        [
            "---",
            "source: wechat",
            f"material_type: {yaml_scalar('微信公众号文章')}",
            f"title: {yaml_scalar(title)}",
            f"source_url: {yaml_scalar(url)}",
            f"author: {yaml_scalar(author)}",
            f"published: {yaml_scalar(published)}",
            f"captured: {yaml_scalar(captured)}",
            "topics: []",
            "hub_topics: []",
            "status: pending",
            "---",
            "",
            f"# {title}",
            "",
            markdown.strip(),
            "",
        ]
    )


def normalize_article(article: Any) -> Any:
    if isinstance(article, dict):
        return article
    if hasattr(article, "model_dump"):
        return article.model_dump()
    if hasattr(article, "__dict__"):
        return vars(article)
    return str(article)


def article_value(article: Any, key: str) -> str:
    if isinstance(article, dict):
        value = article.get(key, "")
    else:
        value = getattr(article, key, "")
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return "\n".join(str(item) for item in value if item is not None).strip()
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value).strip()


def first_non_empty(*values: str) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return ""


def title_from_text(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("http"):
            return stripped.lstrip("#").strip()[:80]
    return ""


def safe_filename(text: str) -> str:
    safe = re.sub(r'[\\/:*?"<>|]+', "-", text).strip(" .")
    return re.sub(r"\s+", " ", safe)[:80] or "wechat-article"


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    for index in range(2, 1000):
        candidate = path.with_name(f"{path.stem}-{index}{path.suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Cannot find unique path for {path}")


def yaml_scalar(value: str) -> str:
    text = str(value).replace("\n", " ").strip()
    if not text:
        return ""
    if re.search(r"[:#\\[\\]{}&,*>!|%@`'\"]|^[-?]|\\s$", text):
        return json.dumps(text, ensure_ascii=False)
    return text
