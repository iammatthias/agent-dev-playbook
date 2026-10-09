# Prompt caching and cost

Sources: "Prompt caching is everything" (Apr 2026); "What a task costs on Opus 5.5" (Sep 2026); Sonnet 5.5 post. Prices are list prices as of Sep 2026 — re-check the pricing page.

## Caching is a prefix match

Everything up to each `cache_control` breakpoint is cached; any byte change invalidates everything after it. Claude Code alerts on cache hit rate and treats drops as incidents.

**Order: static → dynamic**
1. Static system prompt + tools (global)
2. CLAUDE.md / memory (per project)
3. Session context: env, MCP, output style (per session)
4. Messages (grow each turn)

**Ways people break it:** timestamps in the static prompt; nondeterministic tool ordering; editing tool params (e.g. which agents an Agent tool can call); adding/removing tools or MCP servers mid-session; switching models; toggling fast mode; changing effort on Bedrock/Google Cloud/gateways; pausing past the cache lifetime; compaction.

**Patterns**
- Push updates (time, changed files, mode changes) as `<system-reminder>`-style content in the next user message/tool result, not by editing the system prompt.
- Never change the tool set mid-session — use deferred loading stubs (`defer_loading: true` + tool search) and state-transition tools.
- Don't switch models mid-session for a cheap question (rebuilding the cache costs more). Use a subagent with a hand-off message instead.
- **Cache-safe forks:** side calls (compaction, summarization, skill execution) reuse the parent's exact system prompt, tools, and history, then append the new instruction. Reserve a compaction buffer. The API now has built-in compaction.
- Sonnet 5.5 minimum cacheable prompt is 512 tokens. Per-message effort (beta) varies effort without busting the cache; changing top-level effort does bust it.

## What a task costs

Cost ≈ turns × resent context, mostly at cache-read price, plus output (thinking counts as output).

| Opus 5.5 / MTok | Input $4 | Output $20 | Cache read $0.20 | 5-min write 1.25× | 1-hr write 2× |
|---|---|---|---|---|---|
| Sonnet 5.5 | $2 | $10 | $0.20 | $2.50 | $4 |
| Fable 5.1 | $10 | $50 | $0.25 | | |

Fast mode (Opus 5.5): ~2.5× faster, 2× price; first request after enabling pays uncached input on everything — turn it on at session start. Batch API: half price.

**Levers, in order**
1. **Fewer turns** — give a way to self-check (test/build/script); batch tool calls; gather context in one pass. A turn costs everything before it.
2. **High cache hit rate** — 2.8M input tokens: $11.20 uncached vs $1.62 at 90% vs $0.99 at 96%.
3. **Effort before model** — see `models-and-effort.md`.
4. **Trim always-loaded context** — CLAUDE.md <200 lines; disable unused MCP servers (`/mcp`).
5. **Smaller models for lookups only** — subagents that search, read logs, summarize (`model: haiku|sonnet` or `CLAUDE_CODE_SUBAGENT_MODEL`). Keep code edits on the main model; a misread search sends the main model on a costly detour. Agent teams ≈ 7× tokens in plan mode — keep small, shut down when done.

## Session hygiene

- Cache lifetime: 1 h on subscription; 5 min on API key/cloud or when drawing usage credits. Coffee break on API key ⇒ next read becomes a full write.
- `/clear` between unrelated tasks (free). `/compact <what to keep>` at a natural break while the cache is warm (~$0.25 at 150k, pays back in ~10 turns); compacting after a long pause re-reads uncached. `/rewind` to drop a dead end while warm.
- Change model at a break: `/compact` or fresh session with a short plan first, since the new model starts with a cold cache. `/model` persists as default — switch back.
- Read `/usage` (= `/cost`): low cache share → look for pause/model switch/MCP change; high output on a small change → effort too high or retries; total input ≫ conversation size → many turns, find the loop.
- Benchmarks: ~$13/dev/active day enterprise average; 90% under $30.
- Measure on your own work: same real task on two models/effort levels, compare turns, output tokens, cost; 3–4 tasks before concluding. Team-level: Claude Code Analytics API, Usage and Cost API.
