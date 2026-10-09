# Models and effort

Sources: "Spending your effort" (Sep 2026); "What a task costs on Opus 5.5"; "Building with Claude Sonnet 5.5" (Sep 2026); "Getting the most out of Opus 5.5". Model lineup reflects Oct 2026 — verify current IDs.

## Which model

| Work | Model |
|---|---|
| Lookups, search/summarize subagents, log reading, "where is X defined" | Haiku / Sonnet |
| Well-scoped everyday coding, fast iteration, repeated well-defined agent tasks, polished docs/slides/sheets | Sonnet 5.5 (`claude-sonnet-5-5`) |
| Supervised daily driving: multi-file features, debugging, review with edits; long-horizon agentic work | Opus 5.5 (`claude-opus-5-5`) |
| Unsupervised long runs, no existing pattern, large multi-subagent changes | Fable 5.1 |

- Escalate to Fable when Opus 5.5 at xhigh hits the same problem twice; switch back once solved.
- Mechanical edits across many files: keep the main model, set effort low — don't drop to a small model for code.
- `opusplan` (Opus plans, Sonnet edits) inverts this advice — measure before defaulting.

## What effort is

A signal of how much compute to spend — mostly how much verification, edge-case testing, and independent judgment Claude applies. Applies to every output token (thinking, text, tool calls). Higher effort helps most where there are **many hidden edge cases** (sanitizers, storage-engine bugs, solvers, security, hardware, perf); it does **not** fix a wrong approach.

Higher effort on underspecified tasks also means Claude makes more decisions on your behalf; with a detailed spec, effort levels converge.

**Rule of thumb**
- **low** — in-the-loop, quick: brainstorming, sketches, renames, applying known patterns.
- **medium** — most feature work; Opus 5.5 and Claude Code default.
- **high** — verification matters / edge cases: brownfield bug fixes, review. Raise here when medium "fixes one layer".
- **xhigh / max** — fully autonomous hard problems: end-to-end build + verify, security audits. Use only where measured.

**Recommended feature loop:** spec → Claude interviews you for gaps → implement on low → review gist, iterate on low → verify/test on high.

Before raising effort, check whether Claude has a runnable check (e.g. a test through the client catches the second caller at medium). If effort + checks don't work, change model.

Economics: high adding ~20k thinking tokens ≈ $0.40 on Opus 5.5 ≈ one ten-turn retry loop. Worth it only if it saves a retry.

**Effort is recalibrated per model** — never carry a level over. Opus 5.5 thinks more per level than Opus 5. Change mid-session with `/effort <level>` (`/effort status`); keeps cache on API key/subscription, busts it on Bedrock/Google Cloud/gateways.

## Sonnet 5.5 API specifics

- Thinking on by default (adaptive). `thinking: {"type":"disabled"}` → 400. Use `{"type":"between_tools"}` to skip upfront thinking (low/medium/high only; no other fields; effort fixed for the conversation).
- Read response blocks **by type** — may start with `thinking`.
- `tool_choice` `any`/`tool` → 400; use `auto` + `strict: true` tools (`additionalProperties: false` everywhere).
- Conversations append-only; Sonnet 5.5 reads Sonnet 5 thinking blocks, nothing else reads 5.5's.
- Computer use only via `computer_toolset_20260801` (API/Google Cloud); drop old beta headers incl. fine-grained-tool-streaming (use `eager_input_streaming`).
- Advisor tool: Opus 4.8/4.7 and Sonnet 5 rejected as advisors.
- Text between tool calls arrives as progress `thinking` blocks; set `display: "summarized"` or `"updates"` (beta) to render.
- Default effort: high on API, medium in Claude Code. Agentic coding: start medium → high for harder; chat: medium/low. `max_tokens` 128k and stream for agentic coding (thinking counts).
- Lower thinking via effort, not prompt text. Remove old workarounds and re-run evals before tuning.
- At low effort it may skip real checks — add a system-prompt paragraph requiring a real test/type-check/build before reporting done (install declared deps via the project's own package manager, never sudo; otherwise say which check wasn't run).
- Refusals: HTTP 200, `stop_reason: "refusal"`, `stop_details` ∈ cyber, bio, frontier_llm, reasoning_extraction, general_harms. `fallbacks: "default"` (beta) retries cyber/frontier_llm on Sonnet 5.
- High-res images up to 2576px long edge, ~2.5× tokens vs 4.6-era — downscale if detail isn't needed.
- `/claude-api migrate this project to claude-sonnet-5-5` automates migration.
