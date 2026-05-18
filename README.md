# Open Agent Skills

Reusable, privacy-safe Skills for agentic coding workflows and Obsidian knowledge workflows.

This repository is meant to be cloned and used directly. It contains:

- general workflow Skills for planning, debugging, TDD, code review, subagents, and verification
- a generic Obsidian knowledge workflow Skill with optional Feishu/Lark intake
- a cross-platform installer
- safe example configuration files

It does **not** contain API keys, personal vault paths, chat IDs, local service files, or private notes.

## Repository Layout

```text
.
├── agent-workflow-skills/
│   ├── README.md
│   └── skills/
│       ├── using-superpowers/
│       ├── brainstorming/
│       ├── writing-plans/
│       ├── systematic-debugging/
│       ├── test-driven-development/
│       └── ...
├── obsidian-knowledge-flow/
│   ├── SKILL.md
│   ├── README.md
│   ├── requirements.txt
│   └── scripts/
│       ├── classify_materials.py
│       ├── feishu_receiver.py
│       └── sync_topic_hubs.py
├── examples/
│   └── env.example
└── scripts/
    ├── install_skills.py
    └── privacy_scan.py
```

## Requirements

- Git
- Python 3.10 or newer
- An agent runtime that supports filesystem Skills, such as Codex, Claude Code, OpenClaw, or a compatible local agent setup
- Optional for Obsidian classification: an OpenAI-compatible chat-completions API key
- Optional for Feishu/Lark intake: a Feishu/Lark bot app

The core installer uses only the Python standard library.

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

Install all Skills into Codex:

```bash
python scripts/install_skills.py --target ~/.codex/skills
```

Windows PowerShell:

```powershell
py -3 scripts/install_skills.py --target "$env:USERPROFILE\.codex\skills"
```

Verify what would be installed before copying:

```bash
python scripts/install_skills.py --target ~/.codex/skills --dry-run
```

Expected result: the installer lists the workflow Skills plus `obsidian-knowledge-flow`.

## Install Targets

Use the target directory for your agent runtime:

| Runtime | Typical target |
| --- | --- |
| Codex | `~/.codex/skills` |
| Claude Code | `~/.claude/skills` |
| OpenClaw | your OpenClaw workspace `skills/` folder |
| Other local agents | the directory your runtime scans for `SKILL.md` folders |

Windows examples:

```powershell
py -3 scripts/install_skills.py --target "$env:USERPROFILE\.codex\skills"
py -3 scripts/install_skills.py --target "$env:USERPROFILE\.claude\skills"
```

Install only one pack:

```bash
python scripts/install_skills.py --pack agent-workflow-skills --target ~/.codex/skills
python scripts/install_skills.py --pack obsidian-knowledge-flow --target ~/.codex/skills
```

The installer copies only directories containing `SKILL.md`. It skips `.env`, `.git`, caches, logs, databases, and compiled Python files.

## Manual Install

If you do not want to run the installer, copy any Skill folder into your agent's Skills directory.

For the workflow pack:

```bash
mkdir -p ~/.codex/skills
cp -R agent-workflow-skills/skills/* ~/.codex/skills/
```

For the Obsidian Skill:

```bash
cp -R obsidian-knowledge-flow ~/.codex/skills/
```

Windows PowerShell:

```powershell
$target = "$env:USERPROFILE\.codex\skills"
New-Item -ItemType Directory -Force $target
Copy-Item -Recurse .\agent-workflow-skills\skills\* $target
Copy-Item -Recurse .\obsidian-knowledge-flow $target
```

## What The Workflow Skills Do

The `agent-workflow-skills` pack is methodology-focused. It helps an agent behave more like a careful engineering collaborator.

Included Skills:

- `using-superpowers`: check for relevant Skills before starting non-trivial work
- `brainstorming`: turn ambiguous ideas into clear designs
- `writing-plans`: convert approved designs into implementation plans
- `adversarial-plan-review`: review plans from advocate and skeptic perspectives
- `systematic-debugging`: find root cause before changing code
- `test-driven-development`: write failing tests before behavior changes
- `subagent-driven-development`: split approved plans across independent agents
- `dispatching-parallel-agents`: decide when parallel work is appropriate
- `requesting-code-review`: ask for independent review
- `receiving-code-review`: apply review feedback rigorously
- `verification-before-completion`: verify before claiming work is done
- `using-git-worktrees`: isolate feature work
- `executing-plans`: execute written plans with checkpoints
- `finishing-a-development-branch`: finish, merge, or clean up a branch
- `writing-skills`: create and improve Skills

After installation, start a new agent session and ask a non-trivial task. If your runtime exposes Skill metadata, you should see these Skills available.

## Obsidian Knowledge Flow

`obsidian-knowledge-flow` is a generic Skill and script bundle for:

- saving shared links or explicit material messages into an Obsidian inbox
- classifying Markdown notes into `topics` and optional `hub_topics`
- supporting English or Chinese frontmatter fields
- creating topic hub pages
- optionally receiving Feishu/Lark messages

Read the package-specific guide:

```text
obsidian-knowledge-flow/README.md
```

### Minimal Obsidian Setup

Create or choose an Obsidian vault, then copy the example `.env`:

```bash
cp examples/env.example /path/to/vault/.env
```

Windows PowerShell:

```powershell
Copy-Item .\examples\env.example "C:\Path\To\Vault\.env"
```

Fill in:

```text
CLASSIFIER_API_KEY=
CLASSIFIER_BASE_URL=https://api.openai.com/v1
CLASSIFIER_MODEL=gpt-4.1-mini
```

You can use any provider with an OpenAI-compatible `/chat/completions` endpoint.

### First Dry Run

Create a test note:

```bash
mkdir -p /path/to/vault/00_Inbox
cat > /path/to/vault/00_Inbox/example.md <<'EOF'
# Example note

AI tools are changing how small teams plan, debug, and ship software.
EOF
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "C:\Path\To\Vault\00_Inbox"
@"
# Example note

AI tools are changing how small teams plan, debug, and ship software.
"@ | Set-Content -Encoding UTF8 "C:\Path\To\Vault\00_Inbox\example.md"
```

Run dry-run classification:

```bash
python obsidian-knowledge-flow/scripts/classify_materials.py --vault /path/to/vault --folder 00_Inbox --dry-run
```

Windows PowerShell:

```powershell
py -3 .\obsidian-knowledge-flow\scripts\classify_materials.py --vault "C:\Path\To\Vault" --folder 00_Inbox --dry-run
```

If the output looks right, classify for real:

```bash
python obsidian-knowledge-flow/scripts/classify_materials.py --vault /path/to/vault --folder 00_Inbox --limit 5
```

### Chinese Frontmatter

```bash
python obsidian-knowledge-flow/scripts/classify_materials.py \
  --vault /path/to/vault \
  --folder "06_素材库/待分类" \
  --language zh \
  --hub-topics "产品,职业,战略"
```

### Feishu/Lark Intake

Install optional dependency:

```bash
python -m pip install -r obsidian-knowledge-flow/requirements.txt
```

Add these to your vault-local `.env`:

```text
FEISHU_APP_ID=
FEISHU_APP_SECRET=
```

Test without connecting to Feishu/Lark:

```bash
python obsidian-knowledge-flow/scripts/feishu_receiver.py --vault /path/to/vault --simulate-text "save: https://example.com/article"
```

Run the receiver:

```bash
python obsidian-knowledge-flow/scripts/feishu_receiver.py --vault /path/to/vault
```

The public repo intentionally does not include launchd, systemd, Task Scheduler, or machine-specific service files. Add those locally if you want a receiver to run continuously.

## Privacy And Safety

This repo is designed for public sharing. Before publishing your own fork, run:

```bash
python scripts/privacy_scan.py .
```

The scan checks for common private paths, API keys, Feishu/Lark IDs, and local OpenClaw/Codex configuration references.

Do not commit:

- real `.env` files
- API keys, OAuth tokens, or bot secrets
- Feishu/Lark app IDs, app secrets, chat IDs, message IDs, sender IDs, or open IDs
- private Obsidian vault paths
- private diary content, work notes, or scraped article bodies
- machine-specific service files

The Obsidian scripts use conservative defaults:

- long plain text is not saved as material unless it has an explicit save/archive prefix
- Feishu/Lark IDs are not written into notes
- topic page sync only updates generated marker blocks
- hub topics are chosen only from a user-provided allowed list

## Updating Your Installed Skills

Pull the latest repository changes:

```bash
git pull
```

Re-run the installer:

```bash
python scripts/install_skills.py --target ~/.codex/skills
```

The installer replaces existing installed Skill folders with the current repository version.

## Troubleshooting

**`python` is not found**

Use `python3` on macOS/Linux or `py -3` on Windows.

**The agent does not see the Skills**

Check that each installed Skill folder contains a `SKILL.md` directly inside it. Restart the agent session if your runtime loads Skills only at session start.

**Classification says `CLASSIFIER_API_KEY is not set`**

Copy `examples/env.example` to your vault as `.env`, then fill in `CLASSIFIER_API_KEY`. The script reads `<vault>/.env` automatically.

**The classifier API returns an error**

Check that `CLASSIFIER_BASE_URL` points to the provider root ending in `/v1`, and that the selected model supports chat completions and JSON responses.

**Feishu/Lark receiver saves nothing**

Use `--simulate-text` first. Real Feishu/Lark setup also requires app permissions and event subscription configuration in the Feishu/Lark developer console.

## Development Checklist

Before pushing changes:

```bash
python scripts/privacy_scan.py .
python scripts/install_skills.py --target /tmp/open-agent-skills-test --dry-run
python -m py_compile scripts/install_skills.py scripts/privacy_scan.py obsidian-knowledge-flow/scripts/*.py
```

Windows PowerShell:

```powershell
py -3 scripts/privacy_scan.py .
py -3 scripts/install_skills.py --target "$env:TEMP\open-agent-skills-test" --dry-run
py -3 -m py_compile scripts/install_skills.py scripts/privacy_scan.py obsidian-knowledge-flow/scripts/classify_materials.py obsidian-knowledge-flow/scripts/feishu_receiver.py obsidian-knowledge-flow/scripts/sync_topic_hubs.py
```

## License And Attribution

Add a license before publishing derivatives to a package index or marketplace. If you keep upstream-derived Skills, preserve their original license files and attribution.
