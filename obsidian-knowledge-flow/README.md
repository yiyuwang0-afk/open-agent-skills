# Obsidian Knowledge Flow

A generic Skill and script bundle for importing external material into Obsidian, classifying notes with an OpenAI-compatible API, and maintaining topic hub pages.

## Features

- Save shared links or explicit material messages into an Obsidian inbox.
- Classify Markdown notes into open `topics` and optional configured `hub_topics`.
- Support English and Chinese frontmatter field names.
- Create sidebar-visible topic pages from coarse domain/subtopic fields.
- Optionally receive Feishu/Lark bot messages through the official SDK.

## Install

From the public repository root:

```bash
python scripts/install_skills.py --pack obsidian-knowledge-flow --target ~/.codex/skills
```

Windows PowerShell:

```powershell
py -3 scripts/install_skills.py --pack obsidian-knowledge-flow --target "$env:USERPROFILE\.codex\skills"
```

## Configure

Copy the example environment file to your vault:

```bash
cp examples/env.example /path/to/vault/.env
```

Windows PowerShell:

```powershell
Copy-Item .\examples\env.example "C:\Path\To\Vault\.env"
```

Fill in your own values:

```text
CLASSIFIER_API_KEY=
CLASSIFIER_BASE_URL=https://api.openai.com/v1
CLASSIFIER_MODEL=gpt-4.1-mini
FEISHU_APP_ID=
FEISHU_APP_SECRET=
```

Do not commit your real `.env`.

## Classify Notes

Dry run:

```bash
python scripts/classify_materials.py --vault /path/to/vault --folder 00_Inbox --dry-run
```

Classify five notes:

```bash
python scripts/classify_materials.py --vault /path/to/vault --folder 00_Inbox --limit 5
```

Chinese field names:

```bash
python scripts/classify_materials.py --vault /path/to/vault --folder "06_素材库/待分类" --language zh --hub-topics "产品,职业,战略"
```

Windows PowerShell:

```powershell
py -3 .\scripts\classify_materials.py --vault "C:\Path\To\Vault" --folder 00_Inbox --dry-run
```

## Receive Feishu/Lark Messages

Install the optional SDK:

```bash
python -m pip install -r requirements.txt
```

Test without connecting to Feishu/Lark:

```bash
python scripts/feishu_receiver.py --vault /path/to/vault --simulate-text "save: https://example.com/article"
```

Run the receiver:

```bash
python scripts/feishu_receiver.py --vault /path/to/vault
```

The receiver intentionally saves material only. It does not include service-manager files. Use your local platform tools if you want it to run continuously.

## Sync Topic Hub Pages

Dry run:

```bash
python scripts/sync_topic_hubs.py --vault /path/to/vault --dry-run
```

Create or update generated sections:

```bash
python scripts/sync_topic_hubs.py --vault /path/to/vault --topics-folder "05_Topic_Hubs/Content"
```

## Safety Defaults

- Long plain text is not material unless it has an explicit save/archive prefix.
- Message IDs, chat IDs, sender IDs, and local absolute paths are not written into notes.
- `hub_topics` are only selected from a user-provided allowed list.
- Generated topic-page content is updated only inside marker blocks.
- All credentials are read from environment variables or the vault-local `.env`.
