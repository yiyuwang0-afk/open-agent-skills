---
name: obsidian-knowledge-flow
description: Use when setting up or maintaining an Obsidian workflow that imports external material, classifies notes with an LLM, separates open content topics from long-term personal hubs, and keeps topic hub pages automatically updated.
---

# Obsidian Knowledge Flow

Use this skill to build or maintain an Obsidian knowledge workflow with:

- source folders for incoming material
- LLM-assisted classification
- open `topics` for what a note is about
- optional `hub_topics` for long-term thinking areas
- Dataview topic hub pages
- Feishu/Lark forwarding into an Obsidian inbox

## Privacy Rule

Before creating public files, remove user-specific details:

- real vault paths
- API keys, app IDs, secrets, chat IDs, user IDs
- private topic names, private projects, personal diary content
- real article text unless the user explicitly wants examples published

For public skills, use generic examples such as:

```yaml
topics: [AI, business, society]
hub_topics: [career, products, strategy]
```

Do not publish a user's actual long-term themes unless they explicitly approve that exact list.

## Field Model

Use two different topic fields:

```yaml
topics: []      # open content topics, generated from the note itself
hub_topics: []  # optional long-term knowledge hubs defined by the user
```

`topics` may contain broad or specific content themes such as `AI`, `business`, `society`, `media`, `consumer electronics`, or `urban policy`.

`hub_topics` should be chosen only from the user's configured long-term hubs. If a note does not fit any hub, leave it empty.

For Chinese vaults, localized aliases are acceptable:

```yaml
主题: []
长期主题: []
```

Keep existing taxonomy fields if the vault already uses them, such as `domains`, `subtopics`, `tags`, `一级领域`, `二级主题`, or `三级标签`.

## Standard Workflow

1. Inspect the current vault folders and existing frontmatter before editing.
2. Create or confirm these folders:
   - `00_Inbox/`
   - `00_Templates/` or localized equivalent
   - source library folder, such as `06_Sources/`
   - long-term hub folder, such as `05_Topic_Hubs/`
   - project folder, such as `07_Projects/`
3. Add templates that include both `topics` and `hub_topics`.
4. Configure the classifier with:
   - broad content taxonomy for `topics`
   - user-defined long-term hubs for `hub_topics`
5. Update hub pages to query `hub_topics`, not `topics`.
6. Reclassify old material after changing the field model.
7. Run tests or dry-runs before processing a large vault.

## Automation Pattern

Use bundled scripts as starting points:

- `scripts/classify_materials.py`: classify Markdown notes with an OpenAI-compatible chat-completions API.
- `scripts/feishu_receiver.py`: receive Feishu/Lark bot messages and save them to an Obsidian inbox.

Recommended environment variables:

```bash
CLASSIFIER_API_KEY=...
CLASSIFIER_BASE_URL=https://api.example.com
CLASSIFIER_MODEL=example-model
FEISHU_APP_ID=...
FEISHU_APP_SECRET=...
```

Do not hard-code secrets in skill files, scripts, templates, or examples.

## Hub Page Query Pattern

For Dataview, long-term hub pages should query the long-term hub field:

```dataview
TABLE source, type, topics, status
FROM "06_Sources"
WHERE contains(hub_topics, this.file.name)
SORT file.mtime DESC
```

If the vault uses Chinese field names:

```dataview
TABLE 来源, 类型, 主题, 状态
FROM "06_素材库"
WHERE contains(长期主题, this.file.name)
SORT file.mtime DESC
```

## When Reclassifying Existing Notes

Use dry-run first:

```bash
python scripts/classify_materials.py --vault /path/to/vault --folder "06_Sources/Inbox" --dry-run
```

Then process a small batch:

```bash
python scripts/classify_materials.py --vault /path/to/vault --folder "06_Sources/Inbox" --limit 5
```

Only run the whole vault after confirming the output fields are correct.

