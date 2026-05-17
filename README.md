# Public Agent Skills

Reusable, privacy-safe Skills for agentic coding workflows and Obsidian knowledge workflows.

This repository is designed to be shared publicly. It contains no API keys, no personal vault paths, no chat IDs, and no local service configuration.

## What Is Included

- `agent-workflow-skills/`: general-purpose workflow Skills for planning, debugging, test-driven development, code review, subagent work, and completion verification.
- `obsidian-knowledge-flow/`: a generic Obsidian workflow Skill for importing material, classifying notes with an OpenAI-compatible API, syncing topic hub pages, and optionally receiving Feishu/Lark forwarded messages.
- `scripts/install_skills.py`: cross-platform installer that copies selected Skills into a local skills directory.
- `examples/`: safe templates for local configuration.

## Quick Install

Install all Skills into a local directory:

```bash
python scripts/install_skills.py --target ~/.codex/skills
```

Windows PowerShell:

```powershell
py -3 scripts/install_skills.py --target "$env:USERPROFILE\.codex\skills"
```

Install only one pack:

```bash
python scripts/install_skills.py --pack agent-workflow-skills --target ~/.codex/skills
python scripts/install_skills.py --pack obsidian-knowledge-flow --target ~/.codex/skills
```

The installer only copies folders containing `SKILL.md`. It does not copy `.env` files, credentials, local logs, databases, or private vault content.

## Manual Install

Copy any folder that contains a `SKILL.md` file into your agent's skills directory.

Common targets:

- Codex: `~/.codex/skills`
- Claude Code: `~/.claude/skills`
- OpenClaw workspace: your configured OpenClaw workspace `skills/` folder

On Windows, use the same folder structure under your user profile, for example:

```powershell
$target = "$env:USERPROFILE\.codex\skills"
New-Item -ItemType Directory -Force $target
Copy-Item -Recurse .\agent-workflow-skills\skills\* $target
Copy-Item -Recurse .\obsidian-knowledge-flow $target
```

## Obsidian Knowledge Flow Setup

1. Copy `examples/env.example` to `<your-vault>/.env`.
2. Fill in your own API key and model settings.
3. Run a dry run before writing to your vault:

```bash
python obsidian-knowledge-flow/scripts/classify_materials.py --vault /path/to/vault --folder 00_Inbox --dry-run
```

Windows PowerShell:

```powershell
py -3 .\obsidian-knowledge-flow\scripts\classify_materials.py --vault "C:\Path\To\Vault" --folder 00_Inbox --dry-run
```

For Feishu/Lark forwarding, install dependencies and run the receiver:

```bash
python -m pip install -r obsidian-knowledge-flow/requirements.txt
python obsidian-knowledge-flow/scripts/feishu_receiver.py --vault /path/to/vault
```

## Privacy Contract

Before publishing changes, check that the repository does not contain:

- real vault paths
- `.env` files
- API keys or access tokens
- Feishu/Lark app IDs, app secrets, chat IDs, message IDs, sender IDs, or open IDs
- private diary content, private work notes, or scraped article bodies
- local service files such as LaunchAgents, systemd units, or machine-specific OpenClaw config

Run the included lightweight privacy scan:

```bash
python scripts/privacy_scan.py .
```

## Platform Support

The published scripts are written in plain Python and use `pathlib` for paths. They are intended to run on macOS, Windows, and Linux.

Platform-specific service managers are intentionally not included. If you want the Feishu/Lark receiver to run continuously, create your own local launchd, systemd, Task Scheduler, or process-manager setup outside this public repo.

## License

Add a license before publishing to a public package index or GitHub marketplace. If you keep upstream-derived Skills, preserve their original license files and attribution.
