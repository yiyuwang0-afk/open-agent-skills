# Obsidian Knowledge Flow

这个 Skill 的核心用途是：把微信公众号文章和网页素材收进 Obsidian，本地保存为 Markdown，然后用 AI 自动分类，形成可长期复用的素材库。

推荐使用场景：

```text
飞书/Lark 收到微信公众号文章链接
  -> 识别为素材
  -> 用 wechat-article-parser 转成 Markdown
  -> 保存到 Obsidian inbox
  -> classify_materials.py 写入主题、摘要、核心判断
  -> sync_topic_hubs.py 更新主题页
```

它是一个可公开分享的泛化版本，不包含个人 vault 路径、私有主题、API key、chat ID、service 文件或私人笔记。

## What It Does

- 接收 URL 或明确的素材消息。
- 对微信公众号文章链接使用 `wechat-article-parser` 转 Markdown。
- 将 Markdown 文件保存到本地 Obsidian vault。
- 用 OpenAI-compatible API 给笔记补充结构化 frontmatter。
- 支持英文或中文字段。
- 支持长期主题白名单，例如 `产品,职业,战略,AI,写作`。
- 生成 Obsidian 主题页，并只改写自动生成区块。
- 可选接入 Feishu/Lark bot，也可以只用命令行手动导入。

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
    ├── feishu_receiver.py
    ├── wechat_importer.py
    ├── classify_materials.py
    └── sync_topic_hubs.py
```

## Install Dependencies

From the repository root:

```bash
python -m pip install -r obsidian-knowledge-flow/requirements.txt
```

Windows PowerShell:

```powershell
py -3 -m pip install -r .\obsidian-knowledge-flow\requirements.txt
```

Dependencies:

- `lark-oapi`: Feishu/Lark bot event receiver.
- `wechat-article-parser`: WeChat public-account article to Markdown conversion.

If you do not use Feishu/Lark, you can still run the local simulation mode. If you do not import WeChat public-account articles, normal links are saved as simple Markdown notes.

## Configure A Vault

Copy the safe example env file into your own Obsidian vault:

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

For Feishu/Lark intake, also fill in:

```text
FEISHU_APP_ID=
FEISHU_APP_SECRET=
```

Any provider with an OpenAI-compatible `/chat/completions` endpoint should work for classification.

## Recommended Vault Folders

The scripts do not require this exact layout, but it works well:

```text
00_Inbox/
05_Topic_Hubs/
06_Sources/
```

Chinese vault example:

```text
00_Inbox/
05_主题库/
06_素材库/待分类/
```

All folder options are passed as command-line arguments, so Windows and macOS users can keep their own vault layout.

## Import A WeChat Article

Use simulation mode first:

```bash
python obsidian-knowledge-flow/scripts/feishu_receiver.py \
  --vault /path/to/vault \
  --inbox "06_素材库/待分类" \
  --simulate-text "https://mp.weixin.qq.com/s/xxxx"
```

Windows PowerShell:

```powershell
py -3 .\obsidian-knowledge-flow\scripts\feishu_receiver.py `
  --vault "C:\Path\To\Vault" `
  --inbox "06_素材库\待分类" `
  --simulate-text "https://mp.weixin.qq.com/s/xxxx"
```

For `mp.weixin.qq.com` links, the receiver calls `wechat_importer.py`, which uses `wechat-article-parser` and writes a Markdown note with source metadata.

For non-WeChat URLs, the receiver writes a simple Markdown note that preserves the original message and source URL.

## Run Feishu/Lark Intake

After setting `FEISHU_APP_ID` and `FEISHU_APP_SECRET`:

```bash
python obsidian-knowledge-flow/scripts/feishu_receiver.py --vault /path/to/vault --inbox "06_素材库/待分类"
```

The receiver saves only material-like messages:

- any message containing a URL
- messages starting with prefixes such as `save:`, `archive:`, `material:`, `保存素材：`, or `素材：`

This means a WeChat article link can be handled directly, while maintenance instructions such as “重启服务” or “看下日志” are not accidentally archived as notes.

## Classify Notes

Dry run first:

```bash
python obsidian-knowledge-flow/scripts/classify_materials.py \
  --vault /path/to/vault \
  --folder "06_素材库/待分类" \
  --language zh \
  --dry-run
```

Classify five notes for real:

```bash
python obsidian-knowledge-flow/scripts/classify_materials.py \
  --vault /path/to/vault \
  --folder "06_素材库/待分类" \
  --language zh \
  --hub-topics "产品,职业,战略,AI,写作" \
  --limit 5
```

Classify one file:

```bash
python obsidian-knowledge-flow/scripts/classify_materials.py \
  --vault /path/to/vault \
  --file /path/to/vault/06_素材库/待分类/example.md \
  --language zh
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

Create or update generated sections:

```bash
python obsidian-knowledge-flow/scripts/sync_topic_hubs.py \
  --vault /path/to/vault \
  --topics-folder "05_主题库"
```

The sync script only updates content inside marker blocks:

```markdown
<!-- AUTO-GENERATED:START -->
...
<!-- AUTO-GENERATED:END -->
```

Existing pages without markers are reported and left untouched.

## Install As A Skill

From the repository root:

```bash
python scripts/install_skills.py --pack obsidian-knowledge-flow --target ~/.codex/skills
```

Windows PowerShell:

```powershell
py -3 scripts/install_skills.py --pack obsidian-knowledge-flow --target "$env:USERPROFILE\.codex\skills"
```

For OpenClaw or other runtimes, replace the target with the directory your agent scans for `SKILL.md` folders.

## Continuous Running

This public package does not ship service-manager files. To run continuously, create a local service outside this repo:

- macOS: launchd
- Linux: systemd
- Windows: Task Scheduler or a PowerShell profile/process manager

Keep those local service files private if they contain machine-specific paths or secrets.

## Safety Defaults

- Credentials are read only from environment variables or `<vault>/.env`.
- `.env` is ignored by git.
- Local absolute paths are not written to notes.
- Feishu/Lark message IDs, chat IDs, and sender IDs are not written to notes.
- `hub_topics` are only selected from a user-provided allowed list.
- Topic-page sync updates only marker blocks and leaves normal writing alone.

## Troubleshooting

**`wechat_article_parser` import fails**

Run:

```bash
python -m pip install -r obsidian-knowledge-flow/requirements.txt
```

**A WeChat article cannot be parsed**

Check whether the link is a public `mp.weixin.qq.com` article and whether the article can be opened in a normal browser. Some articles may require login, may be removed, or may block automated fetching.

**`CLASSIFIER_API_KEY is not set`**

Copy `examples/env.example` to `<vault>/.env` and fill in `CLASSIFIER_API_KEY`.

**No notes are found**

Check `--vault` and `--folder`. `--folder` is relative to the vault root.

**Feishu/Lark receiver does not get messages**

Verify bot credentials, app permissions, event subscription settings, and whether your app is configured for WebSocket/event delivery.

**The agent does not trigger the Skill**

Confirm that `obsidian-knowledge-flow/SKILL.md` was copied directly under your runtime's Skills directory and restart the agent session if needed.
