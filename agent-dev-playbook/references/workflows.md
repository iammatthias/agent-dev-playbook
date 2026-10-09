# Subagents and dynamic workflows

Source: "A harness for every task: dynamic workflows in Claude Code" (Jun 2026); cost post.

Dynamic workflows: Claude writes a JS harness on the fly using `agent(prompt, {schema, model, isolation: "worktree"|"remote", agentType})`, `parallel()`, `pipeline()`, plus standard JS. Resumable after interruption. Trigger with "use a workflow" or `ultracode`. They cost more tokens — use for complex, high-value tasks.

## Why separate contexts

Counter single-context failure modes: laziness (stopping early), self-preferential bias (judging its own work), goal drift (lossy compaction). Dynamic beats static harnesses because the harness is shaped to this specific task.

## Patterns (compose them)

- **Classify-and-act** — classifier routes to handlers (or decides output).
- **Fan-out-and-synthesize** — one clean context per item; synthesis is a barrier merging structured outputs.
- **Adversarial verification** — a separate agent checks each output against a rubric.
- **Generate-and-filter** — many ideas → rubric/verification → dedupe → best.
- **Tournament** — N attempts, pairwise judging until a winner. Comparative judgment beats absolute scoring.
- **Loop until done** — keep spawning until a stop condition (no new findings / clean logs).

## Use cases

- **Migrations/refactors** — enumerate units (callsites, failing tests, modules); one subagent per fix in a worktree; adversarial reviewer; merge. Tell agents to avoid resource-heavy commands to parallelize more.
- **Deep research / deep verification** — extract every claim; one checker per claim; optional source auditor.
- **Sorting 1000+ items** — tournament or bucket-then-merge; loop holds the bracket, each comparison fresh.
- **Rule adherence** — one verifier per rule + a skeptic to cut false positives. Reverse: mine sessions/review comments for repeated corrections → cluster → verify "would this have prevented a real mistake?" → distill into CLAUDE.md.
- **Root cause** — hypotheses from disjoint evidence (logs vs files vs data), each faces verifiers/refuters. Works for sales drops and pipeline failures too.
- **Triage at scale** — classify, dedupe vs tracker, fix or escalate. Quarantine: untrusted-content readers are read-only and emit summaries; privileged actor only sees summaries. Pair with `/loop`.
- **Exploration & taste** — many solutions + rubric-wielding reviewer or tournament.
- **Lightweight evals** — variants in worktrees, comparison agents grade against rubric (e.g. refining a skill).
- **Model routing** — a classifier researches task shape, routes to Sonnet vs Opus.

## Tips

- Detailed prompts naming the patterns get the best workflows; "quick workflow" works for small adversarial checks.
- `/loop` for recurring runs, `/goal` for hard completion criteria.
- Budget tokens in the prompt ("use 10k tokens").
- Save with `s` in the workflow panel → `~/.claude/workflows`, or ship in a skill as a template.
- Don't use for ordinary coding — most tasks don't need five reviewers. Parallelism must earn its coordination cost.
- Subagents run in their own context and return a summary, but pay for their own tokens; set their model deliberately (see `caching-and-cost.md`).
