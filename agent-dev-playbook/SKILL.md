---
name: agent-dev-playbook
description: Anthropic's own best practices for building with Claude and Claude Code (claude.dev blog corpus, through Oct 2026). Use when writing or trimming CLAUDE.md, skills, system prompts or tool definitions; designing an agent harness or tools; choosing model/effort or cutting cost; setting up prompt caching; planning long runs, subagents or dynamic workflows; building evals or hillclimbing; running a measure-and-optimize loop; writing Claude Code mods; or migrating to Opus 5.5 / Sonnet 5.5.
---

# Agent dev playbook

A distilled corpus of the claude.dev engineering blog. Each reference file is one topic; read only the one(s) the task needs. `sources.md` lists the original posts with URLs and dates — cite or re-fetch them (append `.md` to any post URL for clean markdown) when a detail matters or may have changed.

## Pick a file

| Task / symptom | Read |
|---|---|
| Writing or slimming CLAUDE.md, system prompts, project instructions; old "rules" feel heavy | `references/context-engineering.md` |
| Creating, structuring, or debugging a skill (undertriggering, railroaded, bloated) | `references/skills.md` |
| Designing tools or a harness; deciding add vs. remove a tool; elicitation; search | `references/tools-and-harness.md` |
| Cost spikes, cache misses, compaction, switching models/tools mid-session | `references/caching-and-cost.md` |
| Which model, which effort level, Sonnet 5.5 API migration / breaking changes | `references/models-and-effort.md` |
| Long autonomous runs, when Claude should stop vs. continue, reviewing results | `references/long-runs.md` |
| Parallel work, subagents, dynamic workflows, verification, triage, sorting | `references/workflows.md` |
| Making something measurably faster/better; benchmarks, ratchets, guardrails | `references/measure-and-climb.md` |
| Building an eval, validating a grader, hillclimbing without overfitting | `references/evals.md` |
| Specs, plans, reports, reviews, throwaway editors as HTML instead of Markdown | `references/html-outputs.md` |
| Writing a Claude Code mod (hooks/UI inside a session) | `references/mods.md` |

## Core stance (applies everywhere)

- **Trust judgment over rules.** Claude 5-era models need far less instruction. Anthropic cut ~80% of Claude Code's system prompt with no eval loss. Prefer one line of intent ("match the surrounding code's comment density") over absolute rules that are wrong for some cases.
- **Progressive disclosure.** Keep always-loaded context small; put situational knowledge in files, skills, deferred tools, or subagents that load when needed.
- **Give it a way to check its work.** A runnable test/build/script reduces turns, catches one-layer fixes, and is cheaper than raising effort or changing models.
- **Measure before optimizing.** Anything with a number Claude can move becomes tractable. Validate the number tracks what users feel, then ratchet it in CI.
- **State the goal and constraints, not every step.** Name what "done" looks like and when to stop and ask.
- **Separate contexts fight the long-run failure modes** (stopping early, grading its own work favorably, losing constraints after compaction).

## Gotchas that bite most often

- Leftover "think carefully / step by step" lines: delete them; the models already think. To reduce thinking, lower effort — asking in the prompt doesn't reliably work.
- Don't ask the model to print its internal reasoning in replies — that's a refusal category (`reasoning_extraction`). Use `thinking.display: "summarized"` / `"updates"` or ask for a short rationale instead.
- Anything that changes an earlier part of the request (tools, system prompt, model, MCP servers, fast-mode toggle, effort on Bedrock/Vertex/gateways) busts the prompt cache.
- Effort levels are recalibrated per model; never carry a level over from an older model — re-sweep.
- On Sonnet 5.5: responses can start with a `thinking` block — read content by type, never `content[0].text`.
- A skill's `description` is a trigger spec read by the model, not a human summary.
- Benchmarks drawn only from cases today's model fails measure that model's weaknesses, not your task.
