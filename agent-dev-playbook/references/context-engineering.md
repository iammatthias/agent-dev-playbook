# Context engineering (Claude 5 generation)

Source: "The new rules of context engineering for Claude 5 generation models" (Jul 2026), plus Opus 5.5 guide.

The prompt is a small slice of what Claude sees. The rest — system prompt, CLAUDE.md, skills, memory, references — is general-purpose context that must work across many requests, so it can't be as specific as a prompt.

## Old rule → new rule

| Then | Now | Why |
|---|---|---|
| Give rules | Let Claude use judgment | Hard rules ("never write multi-line comments") are wrong for some prompts and collide with user/skill instructions. Conflicting lines force extra deliberation. |
| Give examples | Design interfaces | Examples narrow the exploration space. A well-typed parameter (e.g. a status enum `pending/in_progress/completed` + "one in_progress at a time") teaches usage implicitly. Claude Code's TodoWrite description went from ~9k chars to a sentence. |
| Put it all upfront | Progressive disclosure | Move situational guidance (code review, verification) into skills; defer tool schemas behind tool search. |
| Repeat yourself | Simple tool descriptions | Tool usage guidance lives in the tool description only, not duplicated in the system prompt. |
| Memory in CLAUDE.md | Auto-memory | Claude saves relevant memories itself now; don't hand-maintain them in CLAUDE.md. |
| Simple specs | Rich references | HTML artifacts, test suites, code to port, and rubrics carry more fidelity than prose markdown specs. |

## Layer by layer

- **System prompt** (only if you build your own harness): product context — what product Claude is in and what it's doing. This is where harness builders should spend effort.
- **CLAUDE.md**: one or two lines on what the repo is for, then spend the tokens on *gotchas* — non-obvious conventions Claude can't infer from the file tree. Don't state what reading the repo reveals. Link to skills for anything situational (e.g. "verification: see the verify skill"). Keep it under ~200 lines; every line is resent every turn.
- **Skills**: lightweight guides for finding information when needed; opinionated, team-specific knowledge. Constrain only where it truly matters. Split long ones into files (see `skills.md`).
- **References** (@-mentioned files): prefer code-shaped references. An HTML mockup beats a description or screenshot of a design; a test suite can *be* the spec.

## Prompt-level habits (Opus/Sonnet 5.5)

- Whole task in one message + finish line + when to stop. E.g. "Done = every endpoint uses the new client, old client deleted, tests pass. Ask me only if a test fails for an unexplained reason."
- Remove "think hard" lines; for quick answers say "answer directly"; control depth with effort.
- Design requests: list the *specific* defaults you don't want (cream backgrounds, italic accent words, "01/02/03" section labels, mono labels, pill buttons). "Avoid generic" just swaps one default for another. Iterate by adding to the list.
- Attach charts/screenshots rather than retyping numbers; ask spatial questions.
- Research: "Mark anything you couldn't confirm and say where you looked."
- Migrating prompts from older models: strip workaround cruft ("do not be lazy", refusal steering, retry shims, mandatory N-step rituals, scratchpad rules, verify-twice rules, contradictory instructions). `/claude-api prompt-audit` and `/doctor` automate this. One benchmark saw ~9% extra cost reduction from the audit alone.
- In long chat projects where follow-ups feel slow, add "treat earlier answers as settled unless I ask or point out a problem." Leave it out of long-analysis projects where later steps may expose earlier errors.

## Simplify pass checklist

1. Find contradictions across system prompt / CLAUDE.md / skills.
2. Delete rules that existed to prevent old-model failure modes; re-run evals.
3. Replace examples with better-typed interfaces.
4. Move situational content into skills or files; leave pointers.
5. Remove duplicated tool guidance.
