# Obsidian Knowledge Flow

A generic Skill and script bundle for importing external material into Obsidian, classifying Markdown notes with an OpenAI-compatible API, and maintaining topic hub pages.

This package is intentionally generic. It does not include personal vault paths, private topics, API keys, Feishu/Lark IDs, or service-manager files.

## What It Does

- Saves shared links or explicitly prefixed material messages into an Obsidian inbox.
- Classifies Markdown notes into open `topics` and optional long-term `hub_topics`.
- Supports English and Chinese frontmatter field names.
- Creates sidebar-visible topic pages from coarse domain/subtopic fields.
- Optionally receives Feishu/Lark bot messages through the official SDK.

## Files

```text
obsidian-knowledge-flow/
├── SKILL.md
├── README.md
├── requirements.txt
├── references/
│   ├── field-model.md
│   └── privacy-checklist.md
└── scripts/
    ├── classify_materials.py
    ├── feishu_receiver.py
    └── sync_topic_hubs.py
```

## Install As A Skill

From the repository root:

```bash
python scripts/install_skills.py --pack obsidian-knowledge-flow --target ~/.codex/skills
```

Windows PowerShell:

```powershell
py -3 scripts/install_skills.py --pack obsidian-knowledge-flow --target "$env:USERPROFILE\.codex\skills"
```

For other runtimes, replace the target with the directory your agent scans for `SKILL.md` folders.

## Configure A Vault

Copy the example environment file to your local vault:

```bash
cp examples/env.example /path/to/vault/.env
```

Windows PowerShell:

```powershell
Copy-Item .\examples\env.example "C:\Path\To\Vault\.env"
```

Fill in classifier settings:

```text
CLASSIFIER_API_KEY=
CLASSIFIER_BASE_URL=https://api.openai.com/v1
CLASSIFIER_MODEL=gpt-4.1-mini
```

Any provider with an OpenAI-compatible `/chat/completions` endpoint should work.

## Recommended Vault Folders

The scripts do not require this exact layout, but these defaults work well:

```text
00_Inbox/
05_Topic_Hubs/
06_Sources/
```

Chinese vault example:

```text
00_Inbox/
05_主题库/
06_素材库/
```

You can pass custom folders with command-line options.

## Classify Notes

Dry run first:

```bash
python obsidian-knowledge-flow/scripts/classify_materials.py \
  --vault /path/to/vault \
  --folder 00_Inbox \
  --dry-run
```

Classify five notes for real:

```bash
python obsidian-knowledge-flow/scripts/classify_materials.py \
  --vault /path/to/vault \
  --folder 00_Inbox \
  --limit 5
```

Classify one file:

```bash
python obsidian-knowledge-flow/scripts/classify_materials.py \
  --vault /path/to/vault \
  --file /path/to/vault/00_Inbox/example.md
```

Windows PowerShell:

```powershell
py -3 .\obsidian-knowledge-flow\scripts\classify_materials.py --vault "C:\Path\To\Vault" --folder 00_Inbox --dry-run
```

## Chinese Field Names

Use `--language zh` to write Chinese metadata fields:

```bash
python obsidian-knowledge-flow/scripts/classify_materials.py \
  --vault /path/to/vault \
  --folder "06_素材库/待分类" \
  --language zh \
  --hub-topics "产品,职业,战略"
```

Chinese fields include:

```yaml
主题: []
长期主题: []
摘要: ""
核心判断: []
使用场景: []
置信度: 0.0
```

## Topic Hub Pages

Dry run:

```bash
python obsidian-knowledge-flow/scripts/sync_topic_hubs.py --vault /path/to/vault --dry-run
```

Create/update generated sections:

```bash
python obsidian-knowledge-flow/scripts/sync_topic_hubs.py \
  --vault /path/to/vault \
  --topics-folder "05_Topic_Hubs/Content"
```

The sync script only updates content inside marker blocks:

```markdown
<!-- AUTO-GENERATED:START -->
...
<!-- AUTO-GENERATED:END -->
```

Existing pages without markers are reported and left untouched.

## Feishu/Lark Intake

Install the optional SDK:

```bash
python -m pip install -r obsidian-knowledge-flow/requirements.txt
```

Add bot credentials to your vault-local `.env`:

```text
FEISHU_APP_ID=
FEISHU_APP_SECRET=
```

Test locally without connecting to Feishu/Lark:

```bash
python obsidian-knowledge-flow/scripts/feishu_receiver.py \
  --vault /path/to/vault \
  --simulate-text "save: https://example.com/article"
```

Run the receiver:

```bash
python obsidian-knowledge-flow/scripts/feishu_receiver.py --vault /path/to/vault
```

The receiver saves only material messages:

- any message containing a URL
- messages starting with prefixes such as `save:`, `archive:`, `material:`, `保存素材：`, or `素材：`

Plain long text is not saved by default. This avoids accidentally archiving maintenance instructions or private conversations.

## Continuous Running

This public package does not ship service-manager files. To run continuously, create a local service outside this repo:

- macOS: launchd
- Linux: systemd
- Windows: Task Scheduler or a PowerShell profile/process manager

Keep those local service files private if they contain machine-specific paths.

## Safety Defaults

- Credentials are read only from environment variables or `<vault>/.env`.
- `.env` is ignored by git.
- Local absolute paths are not written to notes.
- Feishu/Lark message IDs, chat IDs, and sender IDs are not written to notes.
- `hub_topics` are only selected from a user-provided allowed list.
- Topic-page sync avoids diary and private project folders unless you configure it otherwise.

## Troubleshooting

**`CLASSIFIER_API_KEY is not set`**

Copy `examples/env.example` to `<vault>/.env` and fill in `CLASSIFIER_API_KEY`.

**No notes are found**

Check `--vault` and `--folder`. `--folder` is relative to the vault root.

**The API rejects JSON response mode**

Use a model/provider that supports JSON responses, or adapt `classify_materials.py` for your provider.

**Feishu/Lark receiver does not get messages**

Verify bot credentials, app permissions, event subscription settings, and whether your app is configured for WebSocket/event delivery.

**The agent does not trigger the Skill**

Confirm that `obsidian-knowledge-flow/SKILL.md` was copied directly under your runtime's Skills directory and restart the agent session if needed.
