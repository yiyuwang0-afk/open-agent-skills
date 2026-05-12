#!/usr/bin/env python3
"""Generic Feishu/Lark-to-Obsidian receiver.

This script saves incoming bot messages to an Obsidian inbox. It is safe to
publish because all credentials are read from environment variables.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class MaterialMessage:
    text: str
    message_type: str
    message_id: str
    chat_id: str
    sender_id: str
    source_url: str


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Receive Feishu/Lark messages into an Obsidian inbox.")
    parser.add_argument("--vault", required=True, help="Obsidian vault root.")
    parser.add_argument("--inbox", default="00_Inbox", help="Inbox folder relative to the vault.")
    parser.add_argument("--simulate-text", help="Save a local test message without connecting to Feishu.")
    args = parser.parse_args(argv)

    vault = Path(args.vault).expanduser().resolve()
    load_env_file(vault / ".env")
    if args.simulate_text:
        target = save_message(
            vault,
            args.inbox,
            MaterialMessage(
                text=args.simulate_text,
                message_type="text",
                message_id="simulate",
                chat_id="simulate",
                sender_id="simulate",
                source_url=first_url(args.simulate_text),
            ),
        )
        print(f"saved: {target}")
        return 0

    return serve(vault, args.inbox)


def serve(vault: Path, inbox: str) -> int:
    try:
        import lark_oapi as lark
        from lark_oapi.event.dispatcher_handler import P2ImMessageReceiveV1
        from lark_oapi.ws.client import Client as WsClient
    except ImportError as exc:
        raise RuntimeError("Install Feishu SDK first: python -m pip install lark-oapi") from exc

    app_id = os.environ.get("FEISHU_APP_ID", "")
    app_secret = os.environ.get("FEISHU_APP_SECRET", "")
    if not app_id or not app_secret:
        raise RuntimeError("FEISHU_APP_ID and FEISHU_APP_SECRET are required")

    def on_message(event: P2ImMessageReceiveV1) -> None:
        message = extract_message(event)
        target = save_message(vault, inbox, message)
        print(f"saved Feishu message {message.message_id}: {target}")

    event_handler = (
        lark.EventDispatcherHandler.builder("", "")
        .register_p2_im_message_receive_v1(on_message)
        .build()
    )
    client = WsClient(app_id, app_secret, event_handler=event_handler, log_level=lark.LogLevel.INFO)
    print("Feishu receiver started. Press Ctrl+C to stop.")
    client.start()
    return 0


def extract_message(event: Any) -> MaterialMessage:
    event_body = getattr(event, "event", event)
    message = getattr(event_body, "message", None)
    sender = getattr(event_body, "sender", None)
    if message is None:
        raise ValueError("Feishu event does not contain message payload")
    message_type = str(getattr(message, "message_type", "") or "")
    text = content_to_text(message_type, str(getattr(message, "content", "") or ""))
    sender_id = getattr(sender, "sender_id", None)
    return MaterialMessage(
        text=text,
        message_type=message_type,
        message_id=str(getattr(message, "message_id", "") or ""),
        chat_id=str(getattr(message, "chat_id", "") or ""),
        sender_id=str(getattr(sender_id, "open_id", "") or ""),
        source_url=first_url(text),
    )


def save_message(vault: Path, inbox: str, message: MaterialMessage) -> Path:
    folder = vault / inbox
    folder.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    target = unique_path(folder / f"{timestamp}-{safe_filename(title_from_message(message))}.md")
    target.write_text(render_message(message), encoding="utf-8")
    return target


def render_message(message: MaterialMessage) -> str:
    captured = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    title = title_from_message(message)
    return "\n".join(
        [
            "---",
            "source: feishu",
            f"material_type: {yaml_scalar('shared message')}",
            f"title: {yaml_scalar(title)}",
            f"source_url: {yaml_scalar(message.source_url)}",
            f"captured: {yaml_scalar(captured)}",
            f"message_type: {yaml_scalar(message.message_type)}",
            f"message_id: {yaml_scalar(message.message_id)}",
            "topics: []",
            "hub_topics: []",
            "status: pending",
            "---",
            "",
            f"# {title}",
            "",
            message.text.strip(),
            "",
        ]
    )


def content_to_text(message_type: str, raw_content: str) -> str:
    try:
        content = json.loads(raw_content)
    except json.JSONDecodeError:
        return raw_content.strip()
    if message_type == "text":
        return str(content.get("text", "")).strip()
    if message_type == "post":
        return post_content_to_text(content)
    for key in ("text", "title", "file_name", "url"):
        if isinstance(content, dict) and content.get(key):
            return str(content[key]).strip()
    return raw_content.strip()


def post_content_to_text(content: dict[str, Any]) -> str:
    parts: list[str] = []
    for line in content.get("content", []):
        if not isinstance(line, list):
            continue
        line_parts: list[str] = []
        for item in line:
            if not isinstance(item, dict):
                continue
            if item.get("tag") == "a" and item.get("href"):
                line_parts.append(str(item["href"]))
            elif item.get("text"):
                line_parts.append(str(item["text"]))
        if line_parts:
            parts.append(" ".join(line_parts))
    return "\n".join(parts).strip()


def title_from_message(message: MaterialMessage) -> str:
    for line in message.text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("http"):
            return stripped.lstrip("#").strip()[:80]
    return "shared material"


def first_url(text: str) -> str:
    match = re.search(r"https?://\S+", text)
    return match.group(0).rstrip(").,，。") if match else ""


def safe_filename(text: str) -> str:
    safe = re.sub(r'[\\/:*?"<>|]+', "-", text).strip(" .")
    return re.sub(r"\s+", " ", safe)[:80] or "material"


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
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Feishu receiver stopped.", file=sys.stderr)
        raise SystemExit(130)

