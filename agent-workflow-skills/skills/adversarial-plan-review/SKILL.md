---
name: adversarial-plan-review
description: Use when an implementation plan, refactor plan, migration plan, or multi-step execution plan has just been written or found and should be reviewed before execution.
---

# Adversarial Plan Review

## Overview

Review plans by forcing structured disagreement before execution. For each phase or task, dispatch one advocate to defend the plan and one skeptic to attack it, then synthesize a better plan with explicit gates.

Use this after a plan exists and before any implementation begins. The goal is not debate theater; it is to catch hidden behavior changes, missing tests, unsafe staging, cross-platform problems, and unclear execution boundaries.

## When to Use

Use this for:
- implementation plans, refactor plans, migration plans, rollout plans, and multi-step debugging plans
- plans touching user data, filesystem writes, git history, secrets, privacy boundaries, or external services
- plans produced by `writing-plans`
- plans the user asks to "review", "challenge", "argue", "压力测试", "反驳", or "辩护"

Do not use for:
- tiny one-step edits
- pure factual answers
- plans that the user explicitly says to execute immediately without review

## Workflow

1. Read the plan once and identify phases, tasks, or independently reviewable sections.
2. Create a controller checklist:
   - read plan and constraints
   - review each task with advocate and skeptic
   - synthesize revisions
   - decide whether the plan is executable as-is, executable with edits, or blocked
3. Dispatch agents in bounded batches:
   - one advocate per task: defend assumptions, strengths, preserved behavior, and small refinements
   - one skeptic per task: find regressions, missing tests, unsafe commands, hidden coupling, platform issues, and staging risks
4. If the agent limit is reached, close completed agents before spawning more.
5. Do not let review agents edit files unless the user explicitly asks them to.
6. After all task reviews return, dispatch one synthesis agent if available. If not, synthesize inline.
7. Produce a revised plan summary with must-fix changes, per-task revisions, and execution gates.
8. If the original plan file should be updated, edit it only after the user approves or has asked you to persist the revised plan.

## Agent Prompt Pattern

Advocate:

```text
You are the ADVOCATE for Task N of this plan. Do not edit files.
Read <plan path>, focusing on <task name>.
Defend the plan: why this boundary is sound, what assumptions make it safe,
what behavior must be preserved, and what small refinements strengthen it.
Return concise bullets: strengths, defended assumptions, suggested refinements, final verdict.
```

Skeptic:

```text
You are the SKEPTIC for Task N of this plan. Do not edit files.
Read <plan path>, focusing on <task name>.
Attack constructively: find behavior regressions, missing tests, hidden coupling,
privacy or safety leaks, cross-platform issues, staging/commit risks, and unclear boundaries.
Return concise bullets: critical risks, missing checks, better alternatives, final recommendation.
```

Synthesis:

```text
You are the FINAL SYNTHESIS agent for this plan debate. Do not edit files.
Read <plan path> and synthesize the advocate/skeptic findings into a better plan.
Preserve the original goal and phase structure where possible.
Return a revised plan, not a transcript.
```

## Review Checklist

For every task, check:
- Behavior parity: does "refactor" secretly change outputs, defaults, file formats, or CLI semantics?
- Test coverage: are failing/parity/safety tests written before implementation?
- Data safety: could content files, private notes, secrets, logs, or runtime files be modified or staged?
- Git hygiene: is each commit scoped, with explicit staged-file checks?
- Cross-platform support: are paths, subprocesses, shells, and filenames portable across macOS and Windows?
- External effects: could the task call APIs, sync, publish, delete, reclassify, or batch-write unexpectedly?
- Import and CLI boundaries: do direct entrypoints still work after extraction?
- Memory and handoff: will future sessions know what changed, what was excluded, and what remains?

## Output Format

Keep the final answer compact:

```markdown
**Verdict**
Executable as-is / executable after revisions / blocked.

**Must Fix Before Execution**
- ...

**Per-Task Revisions**
- Task 1: ...
- Task 2: ...

**Execution Gates**
- ...
```

## Common Mistakes

- Treating advocate/skeptic output as the final answer. Always synthesize.
- Letting agents implement while reviewing. Review first, execute later.
- Opening too many agents at once. Batch them and close completed agents.
- Accepting generic skepticism. Require concrete tests, commands, or plan edits.
- Forgetting to update the original plan after the user approves revisions.
