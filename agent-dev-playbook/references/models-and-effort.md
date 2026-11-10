# Models and effort

Sources: "Which Claude model should you build with?" (Nov 2026); "Spending your effort" (Sep 2026); "What a task costs on Opus 5.5"; "Building with Claude Sonnet 5.5" (Sep 2026); "Getting the most out of Opus 5.5". Model lineup reflects Nov 2026 — verify current IDs.

## Which model

| Work | Model |
|---|---|
| Lookups, search/summarize subagents, log reading, "where is X defined" | Haiku / Sonnet |
| Well-scoped everyday coding, fast iteration, repeated well-defined agent tasks, polished docs/slides/sheets | Sonnet 5.5 (`claude-sonnet-5-5`) |
| Supervised daily driving: multi-file features, debugging, review with edits; long-horizon agentic work | Opus 5.5 (`claude-opus-5-5`) |
| Unsupervised long runs, no existing pattern, large migrations/refactors, leading many subagents, deep research, hardest coding/finance/science | Fable 5.2 (`claude-fable-5-2`) |
| Classification, routing, extraction at volume; cheap subagents | Haiku 5.5 (`claude-haiku-5-5`) |

- Default: start on Opus 5.5 at `medium`. Clear spec ≠ Sonnet: migrations/perf work can be hard enough for Opus or Fable.
- Escalate to Fable when Opus 5.5 at `high` still falls short (or xhigh hits the same problem twice); before pushing Opus past `high`, test Fable 5.2 at lower effort; switch back once solved.
- Past `high`, one more effort level can cost as much as a bigger model — compare both. FrontierCode 2.0: Fable 5.2 `high` ≈ Opus 5.5 `max` (45.3 vs 45.5%) at ~half the cost/task. Terminal-Bench 3.0: Fable 5.1 `max` 58.0% < Opus 5.5 `high` 58.9% at 2× tokens.
- Escalation order when a model isn't good enough: (1) give it self-verification, (2) raise effort one level, (3) next model up at *lower* effort.
- Cheapest pattern when outcomes are checkable: run everything at `low`, re-run failures at `high` (SWE-bench Pro subset, Opus 5.5: ~97% at ~$0.17/task vs 95.3% at $0.29 all-`high`). Opus 5.5 `medium` ≈ −2.5 pts at ~70% of `high` cost; `low` ≈ −8 pts at ~⅓; `xhigh` ≈ +1.4 pts at 2.5×.

## Lineup (API list prices, per M tokens)

| | Haiku 5.5 | Sonnet 5.5 | Opus 5.5 | Fable 5.2 |
|---|---|---|---|---|
| In / out | $0.10/$0.50 (≤100K prompt), $0.50/$2.50 (>100K) | $2/$10 | $4/$20 | $8/$40 |
| Cache read | $0.01 / $0.05 | $0.10 | $0.20 | $0.20 |
| Default effort (API) | medium | high (medium in CC) | medium | high (medium in CC) |
| Thinking | adaptive, can disable (effort ≤ high) | adaptive, `between_tools` | always on | always on |
| Fast mode | no | no | yes | yes |

All: 1M context, 128K max output. Fable 5.2 output ~30% faster than 5.1; Sonnet 5.5 ~30% faster than Sonnet 5. Haiku is the only model with prompt-length pricing — wins on short prompts (¹⁄₂₀ Sonnet input); for long prompts compare cost per finished task. On long runs Fable vs Opus differs only on uncached input/output (2×), since cache reads are equal. Price the hardest tasks, not typical ones (on one benchmark 2 of 20 problems = 43% of spend). Chat/interactive: Sonnet 5.5 at low/medium.

## Mixing models

- Switch at a natural break: cache belongs to the model that wrote it (first turn pays full cache write) — `/compact` or fresh session with a short plan; on API open with a summary.
- Thinking blocks are model-tagged; unreadable ones are silently dropped (request succeeds, reasoning lost). Readers: Opus 5.5 reads Sonnet 5.5/Haiku 5.5; Sonnet reads Haiku; Fable 5.2 reads Opus/Sonnet/Haiku. Moving down a tier, or from Fable 5.2 to anything else, loses reasoning.
- Subagents: `model: haiku|sonnet` in definition or `CLAUDE_CODE_SUBAGENT_MODEL`. Keep small models on cheap-to-check work (find files, run tests, read logs); edits/judgment stay on main. Built-in Explore now runs on the session model (capped at Opus on API) — define your own `Explore` with `model: haiku` to keep it cheap. `haiku` alias → Haiku 5.5 on Anthropic API (needs Claude Code ≥ v2.1.293); still Haiku 4.5 on Bedrock/Google Cloud/Foundry/AWS. Pin with `ANTHROPIC_DEFAULT_HAIKU_MODEL`.
- Keep the big model's context lean — it's paid every turn; let cheap subagents do verbose reading.
- Advisor tool (beta): cheap executor + stronger advisor it consults. Weak evidence: Opus 5.5 `high` + Fable 5.1 advisor = +1.7 pts for 2.1× cost (noise-level). Measure the executor's consult rate first; check accepted advisors (Sonnet 5.5 accepts Fable 5.2/Opus 5.5/Opus 5/Sonnet 5.5; Fable 5.2 accepts only Fable 5.2/Mythos 5.2).
- Bulk work beyond one context: top model leads, ≤25 cheaper parallel workers (Opus lead + Sonnet workers on ~22M tokens of source: ~⅓ cheaper, same score). Skip for one dependent chain or work that fits one context. Managed Agents multiagent orchestration provides coordinator + roster.
- Compatibility for mixed systems — build for the strictest: append-only history (Fable 5.2 preserved thinking → 400 if anything before a thinking block changes, unless you opt in to dropping; none needed via Claude Code/Agent SDK/Managed Agents), `tool_choice: auto` + strict tools, read blocks by `type`, precise prompts. Route by code, not by a model, when the rule is simple.
- Haiku 4.5 → 5.5: replace `budget_tokens` with effort; drop non-default `temperature`/`top_p`/`top_k` (400); end `messages` with a user turn (trailing assistant → 400).
- Safety fallbacks (Opus 5.5/Sonnet 5.5/Fable 5.2 classifiers, mostly cyber/bio): in Claude Code flagged requests may re-run on an older model, noted in transcript — cyber → Opus 4.8, bio → Opus 5.
- Pick by your data: sample real tasks with outcome checks, 2–3 efforts per model in separate sessions, cost from `usage`, plot score vs spend; keep a multi-model setup only if it beats every single-model point; shadow-run before cutover. Quick CC check: same task on two models via `/model`, compare `/usage`.
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
