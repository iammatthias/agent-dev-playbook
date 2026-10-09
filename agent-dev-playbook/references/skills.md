# Skills

Sources: "Lessons from building Claude Code: How we use skills" (Jun 2026); context-engineering post; dynamic workflows post.

A skill is a **folder**, not a markdown file: instructions, scripts, assets, data, config, even hooks. Treat the whole file tree as context engineering.

## Pick one category (straddling several confuses the agent)

1. **Library/API reference** — correct use of an internal lib/CLI/SDK; reference snippets + gotchas.
2. **Product verification** — drive and assert on the real product (Playwright, tmux, headless flows, video capture, per-step state assertions). *Highest measured impact on output quality — worth an engineer-week to make excellent.*
3. **Data fetching & analysis** — credentials, dashboard IDs, canonical tables/joins, field-name mappings.
4. **Business/team automation** — one-command workflows (standup, tickets, recaps); keep a log of past runs.
5. **Scaffolding/templates** — boilerplate with natural-language requirements code can't encode.
6. **Code quality & review** — style Claude misses by default, test practices, adversarial review subagent; can run via hooks/CI.
7. **CI/CD & deploy** — babysit PRs, gradual rollout with auto-rollback, cherry-pick in worktrees.
8. **Runbooks** — symptom → tools → query patterns → structured report.
9. **Infra ops** — routine/destructive maintenance with guardrails (soak periods, confirmation).

## Writing it

- **Don't state the obvious.** Only include what pushes Claude off its defaults or what it can't infer from the repo.
- **Gotchas section = highest signal.** Grow it from real failures over time (append-only tables, field aliases across services, staging returning 200 when the webhook didn't process).
- **Progressive disclosure via files.** SKILL.md is a hub with a symptom → file table; details live in `references/*.md`, templates in `assets/`, helpers in `scripts/` or `lib/`. Tell Claude what files exist.
- **Don't railroad.** State goal + constraints, not every command. ("Cherry-pick onto a clean branch, resolve conflicts preserving intent; if it can't land cleanly, explain why.")
- **Description is a trigger spec for the model.** Say *when* to use it and include trigger phrases ("babysit", "watch CI", "make sure this lands"), not a marketing summary.
- **Setup via config.** Store user-specific setup in `config.json` in the skill dir; if missing, ask (AskUserQuestion for structured choices) and save.
- **Memory inside the skill.** Append-only log / JSON / SQLite so the next run knows what changed. Use `${CLAUDE_PLUGIN_DATA}` for a stable data dir.
- **Ship code, not boilerplate instructions.** A small helper library with gotchas in docstrings lets Claude spend turns composing one-off scripts.
- **On-demand hooks.** Skill-scoped hooks active only when invoked: e.g. `/careful` blocks `rm -rf`, `DROP TABLE`, force-push, `kubectl delete`; `/freeze` blocks edits outside one directory.
- **Workflow templates.** Dynamic-workflow `.workflow.js` files can live in the skill; tell Claude to treat them as templates, not verbatim scripts.
- **Compose by name.** Reference other skills by name; Claude invokes them if installed.

## Distribution & measurement

- Small team/few repos: check in under `./.claude/skills` (each adds a bit of context).
- Scale: plugin marketplace so people opt in; promote organically (sandbox folder → traction → PR into marketplace).
- Log skill usage with a PreToolUse hook to find undertriggering skills.
- Hillclimb trigger rate by editing the description against an eval (see `evals.md`).
- Start with a few lines and one gotcha; improve as Claude hits edge cases. `/doctor` helps right-size.
