# Obsidian WeChat Knowledge Flow

把微信公众号文章、网页链接和临时素材收进 Obsidian，转换成 Markdown，交给 AI 分类，最后沉淀成本地可检索的知识库。

这个仓库的主用途不是一个“大而全的 agent skills 合集”，而是一套可公开分享、隐私安全、跨平台的 Obsidian 知识流模板。它适合你想把微信文章或网页资料长期保存到自己的本地 Obsidian vault，而不是散落在聊天窗口、收藏夹或稍后读工具里的场景。

## It Solves This

- 在飞书/Lark 里收到一条微信公众号文章链接，例如 `https://mp.weixin.qq.com/...`。
- 自动识别它是素材，不需要额外确认或再回复一句“请分类”。
- 用 `wechat-article-parser` 把微信公众号文章转换成 Markdown。
- 把文章保存到你的本地 Obsidian vault，而不是上传到第三方知识库。
- 用 OpenAI-compatible API 给 Markdown 笔记补充主题、长期主题、摘要、核心判断、使用场景等 frontmatter。
- 根据主题生成或更新 Obsidian 主题页，方便后续回看和复用。

简单说，它是：

```text
微信公众号文章链接
  -> Markdown 转换
  -> Obsidian 本地保存
  -> AI 自动分类
  -> 主题页/素材库沉淀
```

## What Is Included

```text
.
├── obsidian-knowledge-flow/
│   ├── SKILL.md
│   ├── README.md
│   ├── requirements.txt
│   └── scripts/
│       ├── feishu_receiver.py      # Feishu/Lark intake, link detection
│       ├── wechat_importer.py      # WeChat article -> Markdown importer
│       ├── classify_materials.py   # AI classification for Markdown notes
│       └── sync_topic_hubs.py      # topic hub page generation
├── agent-workflow-skills/
│   └── skills/                     # optional agent workflow methods
├── examples/
│   └── env.example                 # safe config template
└── scripts/
    ├── install_skills.py
    └── privacy_scan.py
```

The `agent-workflow-skills` folder is optional. It contains planning, debugging, TDD, review, and verification workflows for coding agents. The Obsidian workflow can be used without adopting those methodology Skills.

## What Is Not Included

This public repository intentionally does not include:

- API keys
- personal Obsidian vault paths
- private topics or private notes
- Feishu/Lark chat IDs, sender IDs, app secrets, or message IDs
- local launchd/systemd/Task Scheduler files
- any private automation service configuration

You add those in your own local `.env` and local service manager.

## Requirements

- Git
- Python 3.10 or newer
- Obsidian
- Optional: Feishu/Lark bot app for message intake
- Optional: OpenAI-compatible chat-completions API for classification

Python dependencies for the Obsidian flow:

```text
lark-oapi
wechat-article-parser
```

`wechat-article-parser` is the package used for the WeChat public-account article to Markdown step.

## Quick Start

Clone the repository:

```bash
git clone https://github.com/yiyuwang0-afk/open-agent-skills.git
cd open-agent-skills
```

Windows PowerShell:

```powershell
git clone https://github.com/yiyuwang0-afk/open-agent-skills.git
cd open-agent-skills
```

Install Python dependencies:

```bash
python -m pip install -r obsidian-knowledge-flow/requirements.txt
```

Windows PowerShell:

```powershell
py -3 -m pip install -r .\obsidian-knowledge-flow\requirements.txt
```

Copy the example env file into your Obsidian vault:

```bash
cp examples/env.example /path/to/your/vault/.env
```

Windows PowerShell:

```powershell
Copy-Item .\examples\env.example "C:\Path\To\Your\Vault\.env"
```

Fill in the values you use:

```text
CLASSIFIER_API_KEY=
CLASSIFIER_BASE_URL=https://api.openai.com/v1
CLASSIFIER_MODEL=gpt-4.1-mini

FEISHU_APP_ID=
FEISHU_APP_SECRET=
```

Any provider with an OpenAI-compatible `/chat/completions` endpoint can be used for classification.

## Try It Without Feishu/Lark

You can simulate a received WeChat article link locally:

```bash
python obsidian-knowledge-flow/scripts/feishu_receiver.py \
  --vault /path/to/your/vault \
  --inbox "06_素材库/待分类" \
  --simulate-text "https://mp.weixin.qq.com/s/xxxx"
```

Windows PowerShell:

```powershell
py -3 .\obsidian-knowledge-flow\scripts\feishu_receiver.py `
  --vault "C:\Path\To\Your\Vault" `
  --inbox "06_素材库\待分类" `
  --simulate-text "https://mp.weixin.qq.com/s/xxxx"
```

If the URL is a WeChat public-account article, the receiver calls the WeChat importer and saves a Markdown note. For normal links or text material, it saves a simpler Markdown note with source metadata.

## Classify Saved Notes

Dry run first:

```bash
python obsidian-knowledge-flow/scripts/classify_materials.py \
  --vault /path/to/your/vault \
  --folder "06_素材库/待分类" \
  --language zh \
  --dry-run
```

Classify for real:

```bash
python obsidian-knowledge-flow/scripts/classify_materials.py \
  --vault /path/to/your/vault \
  --folder "06_素材库/待分类" \
  --language zh \
  --hub-topics "产品,职业,战略,AI,写作" \
  --limit 10
```

The classifier writes metadata into the Markdown file, so the result stays local in your vault.

## Generate Topic Hubs

```bash
python obsidian-knowledge-flow/scripts/sync_topic_hubs.py \
  --vault /path/to/your/vault \
  --topics-folder "05_主题库"
```

The sync script only rewrites generated marker blocks:

```markdown
<!-- AUTO-GENERATED:START -->
...
<!-- AUTO-GENERATED:END -->
```

Your hand-written notes outside those blocks are left alone.

## Install As Agent Skills

If your agent runtime supports filesystem Skills, install the Obsidian skill:

```bash
python scripts/install_skills.py --pack obsidian-knowledge-flow --target ~/.codex/skills
```

Windows PowerShell:

```powershell
py -3 scripts/install_skills.py --pack obsidian-knowledge-flow --target "$env:USERPROFILE\.codex\skills"
```

Typical targets:

| Runtime | Typical target |
| --- | --- |
| Codex | `~/.codex/skills` |
| Claude Code | `~/.claude/skills` |
| OpenClaw | your OpenClaw workspace `skills/` folder |
| Other local agents | the directory your runtime scans for `SKILL.md` folders |

Install the optional coding workflow Skills only if you want them:

```bash
python scripts/install_skills.py --pack agent-workflow-skills --target ~/.codex/skills
```

## Continuous Running

This repo does not ship machine-specific service files. To keep the receiver running continuously, create a local service outside the repo:

- macOS: launchd
- Linux: systemd
- Windows: Task Scheduler or your preferred process manager

Keep those service files private if they contain absolute paths, tokens, or local machine names.

## Privacy Defaults

- `.env` is ignored by git.
- Credentials are read from environment variables or `<vault>/.env`.
- Feishu/Lark IDs are not written into notes.
- Local absolute paths are not written into notes.
- The public examples use placeholder folders and placeholder config values.
- A privacy scan script is included before publishing changes:

```bash
python scripts/privacy_scan.py .
```

## More Detail

Read the Obsidian-specific guide here:

[obsidian-knowledge-flow/README.md](obsidian-knowledge-flow/README.md)
