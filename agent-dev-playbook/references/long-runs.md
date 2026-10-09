# Long autonomous runs

Sources: "Getting the most out of Opus 5.5" (Sep 2026); dynamic workflows post; cost post.

## Kick-off

One message: the whole task, the finish line, and when to stop.

```
Migrate the payment endpoints from the old client to the new one.
Done means: every endpoint uses the new client, the old client is deleted, and the test suite passes.
Stop and ask me only if a test fails for a reason you can't explain.
```

## CLAUDE.md stop rule

```
When a step doesn't need my input, keep going. Put status notes in the same message as your next action.
Stop and ask only when you can't continue without me, or before anything destructive: deleting data, force-pushing, or changing anything outside this repository.
```

Keep permission prompts on for destructive commands regardless. For pair-programming, invert it: one-line plan up front, short recap at end. If runs keep stopping with "want me to continue?", reply "continue" and add the rule.

## During the run

- Type follow-ups while it works instead of restarting (restarts are expensive on long runs).
- Keep the task list in a file (`TASKS.md`: tick items, add discoveries) — survives compaction; read it instead of scrollback.
- Split audits/migrations across subagents and check each one's evidence before accepting; finish with one table.
- Set report format in CLAUDE.md, e.g. "End every run with: Blocked on me, Changed, Found."

## Failure modes in a single context

- **Agentic laziness** — declares done after partial progress (35/50 items).
- **Self-preferential bias** — grades its own findings favorably.
- **Goal drift** — constraints lost across turns/compaction.

Mitigate with file-based task lists, finish lines, `/goal` hard completion requirements, and separate-context workflows (`workflows.md`).

## Reviewing results

1. Read what it needs from you first (open decisions, approvals), then the summary.
2. Run a review pass before a human: "Review the diff on this branch against main. List only problems you'd block the merge for: file and line, why it's wrong, how to show it fails."
3. For research: require marking what couldn't be confirmed and where it looked.
4. Long-document QA: "Check this for anything that contradicts itself: numbers, dates and names. Quote each problem and say where."
