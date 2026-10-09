# Tools and harness design

Sources: "Seeing like an agent" (Apr 2026); context-engineering post; prompt-caching post.

**See like an agent:** give tools shaped to the model's abilities (paper → calculator → computer). Learn those abilities by reading transcripts and experimenting.

## Principles

- **Prefer a tool over an output-format convention when you need structure.** Claude Code's AskUserQuestion evolution: bolting questions onto ExitPlan confused intent; a parsed markdown convention was unreliable (dropped options, extra prose); a dedicated tool that blocks the loop and renders a modal worked — and was composable (SDK, skills). Check Claude *likes* calling it.
- **Revisit tools as models improve.** TodoWrite + reminders every 5 turns helped weaker models; stronger ones felt boxed in by reminders. Replaced by Tasks (dependencies, shared across subagents, editable/deletable). Support a small set of similarly-capable models so tool assumptions hold.
- **Let Claude find its own context.** Grep/search beat pre-indexed RAG: no setup, robust across environments, model-driven. Skills formalize nested progressive disclosure.
- **High bar for new tools** (~20 in Claude Code). Each is another option to weigh. Alternatives:
  - progressive disclosure (docs/skill files loaded on demand)
  - a **subagent** that does the noisy lookup in its own context and returns only the answer (Claude Code Guide pattern)
  - deferred tool loading behind tool search
- **Model state transitions as tools, not tool-set swaps.** Plan mode = EnterPlanMode/ExitPlanMode tools + a system message; tool definitions never change (cache-safe, and the model can enter plan mode itself).
- **Interface over examples.** Expressive parameters (enums, required fields, strict schemas with `additionalProperties: false`) teach usage better than example blocks. Keep usage guidance in the tool description, not duplicated in the system prompt.
- **Forced tool choice is gone on Sonnet 5.5** (`any`/`tool` → 400). Use `tool_choice: auto` + `strict: true` + say in the prompt when to use it.

## Harness choices

- Default single-context harness works for most coding.
- Build/generate a custom harness (dynamic workflows, Agent SDK, `claude -p`) for long-running, massively parallel, highly structured, or adversarial tasks — see `workflows.md`.
- Quarantine pattern: agents that read untrusted content get read-only tools and emit structured summaries; a separate privileged agent acts on summaries.
- Design the whole harness around prompt caching from day one — see `caching-and-cost.md`.
