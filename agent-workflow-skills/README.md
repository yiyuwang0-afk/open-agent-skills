# Agent Workflow Skills

General-purpose workflow Skills for agentic coding and writing work.

## Included Skills

- `using-superpowers`: check and load relevant workflow Skills before starting non-trivial tasks.
- `brainstorming`: clarify ambiguous feature, UX, behavior, and architecture work before implementation.
- `writing-plans`: turn approved designs or requirements into execution plans.
- `adversarial-plan-review`: review implementation plans with advocate/skeptic perspectives before execution.
- `systematic-debugging`: find root cause before changing code.
- `test-driven-development`: write a failing test before changing behavior.
- `subagent-driven-development`: split approved implementation plans across independent agents.
- `dispatching-parallel-agents`: decide when independent tasks can run in parallel.
- `requesting-code-review`: request independent review before merging or continuing.
- `receiving-code-review`: evaluate and apply review feedback rigorously.
- `verification-before-completion`: verify before claiming work is complete.
- `finishing-a-development-branch`: choose merge, PR, or cleanup path after implementation.
- `using-git-worktrees`: isolate feature work in git worktrees.
- `executing-plans`: execute written plans with checkpoints.
- `writing-skills`: create and maintain high-quality Skills.

## Install

From the repository root:

```bash
python scripts/install_skills.py --pack agent-workflow-skills --target ~/.codex/skills
```

Windows PowerShell:

```powershell
py -3 scripts/install_skills.py --pack agent-workflow-skills --target "$env:USERPROFILE\.codex\skills"
```

## Notes

These Skills are methodology-focused. They do not require a specific operating system, API provider, or local file path.

Some examples mention common Unix-style paths such as `~/.codex/skills` or `~/.claude/skills`. On Windows, install to the equivalent folder under your user profile.
