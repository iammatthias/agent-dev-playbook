# Measure-and-climb loop (performance and beyond)

Sources: "How we made claude.ai 3x faster in two weeks" (Sep 2026) — 13 journey measurements, 3.1× geomean faster, 3,000+ changes, zero customer incidents or rollbacks; "Using a 'chaos loop' to harden the Claude Docs launch" (Nov 2026) — see last section.

**Central lesson: with Claude, measuring something makes it tractable.** Measurement is step one of the climb, not step zero. The highest-leverage human activity is finding more things to measure.

## Setup

- Standing brief for the agent: scope of responsibility (monitor deploys, audit telemetry, curate dashboards, fix low-hanging fruit, propose projects, communicate), and an explicit aspiration toward autonomy.
- Let Claude pick the highest-impact journeys from real usage data (e.g. via a Datadog MCP). Instrument until measurements are comparable: start at user interaction, end at render, separate client vs server.
- Seed ~20 projects; have Claude estimate impact in ms; aggregate into targets. Leave room for Claude-proposed workstreams.

## Lab benchmarks that beat wall-clock noise

Deterministic proxies Claude can climb overnight without waiting for field data:
- JS instruction counts under Valgrind with `node --predictable` (`Ir`) against a checked-in baseline — one run, no stats.
- V8 precise-coverage call counts, React commits per interaction, style recalcs, layout counts, DOM mutations.
- Layout Instability API sources mapped to named regions/phases (CLS was too coarse).
- Deterministic 120 Hz frame stepping in headless Chrome via DevTools begin-frame control → exact "did this frame fit 8.33 ms".

**Every benchmark has two jobs:** a metric to climb in the lab, and a CI guardrail that only ratchets down. **Prove it correlates** with user-felt latency (e.g. −48% instructions → −78% wall clock) or unship it. Flaky or uncorrelated ⇒ thrown out.

## The per-thread loop

1. Open a narrow thread on one slow stretch (screenshot/recording).
2. Claude traces the flow and finds/builds a benchmark that reproduces it (e.g. test red 20/20 on main, green 20/20 on PR).
3. PRs sized for risk and review; user-visible changes behind flags.
4. Ship, then Claude watches the deploy and reads field data by build/platform.
5. Win → ratchet the benchmark ceiling down (daily job lowers it). No win → flag off, iterate.
6. Look for the next slow spot in the same journey. Threads don't close at the first fix.

Scale horizontally: many narrow threads (150+ concurrent). Claude increasingly opens threads itself from nightly jobs. ~1/3 of PRs added telemetry or guardrails.

## Guardrails

- Automated review + at least one human approval on every PR.
- Unit tests before optimizations.
- Short-lived feature flags for anything user-visible; Claude classifies each as kill switch vs ramp and retires them promptly.
- Protect brittle wins with dedicated tests (e.g. static markup generated from the real component; pixel-alignment checks across 14 viewports; keystroke-through-handoff test; field telemetry to 0.1 px with auto-opened threads).
- Incremental rollout: employees → 1% → everyone; dogfooding catches what lab can't.

## Steering (the human job)

- **Ambition** — Claude defaults to cautious scope and padded estimates; explicitly push: "targets are not the stopping point", "be braver".
- **Taste** — named human owner per thread; Claude shows before/after recordings of any user-perceptible change for a ruling.
- **Direction** — keep threads narrow; sequence, merge overlapping threads, close at diminishing returns, veto complexity that isn't worth it ("2 ms per send isn't worth maintaining this build plugin").

## Finds worth remembering

Repeated megamorphic lookups of the same ID; 6,900 hooks re-rendering per keystroke; one `:root:has()` selector costing 24 ms per DOM change; a stray `location.reload()`; redundant IndexedDB clones on main thread; non-Latin-1 chars (em dashes) forcing V8 two-byte strings onto slow regex paths; Chrome prerender height mismatch from managed-browser footers.

## Chaos loop (same climb, for reliability and scale)

Claude Docs launch: single-node proof of concept → 4.6M docs in 6 days, 60 server errors in 2B requests, 629 prod rolls in the month, no rollbacks, ~50 pods. One engineer, two weeks of a continuously running loop on staging.

**The loop:** pick a scenario → harness pushes one feature to saturation and breaks things → Claude reads telemetry (observability MCP) → short menu of options + a recommendation → easy to undo: Claude writes it, a separate session reviews it, deploy to staging, rerun; hard to undo: stop and ask.

- **Staging mirrors production at launch scale**, driven by synthetic load (~10× real traffic is a good start). A few thousand real users on one machine say nothing about launch.
- **Pick scenarios that feel paranoid:** 10M docs created in a day; 22,000 connections reconnecting at once; one hot doc with hundreds of viewers; a server killed mid-load; the database stalling; a deploy in the middle of a spike. 7 of 10 rehearsed scenarios then happened in prod.
- **Write the invariants down before starting** and hand them to Claude (theirs: docs open near-instantly even with long history; an acknowledged edit is never lost). Tests check them every iteration.
- **Name the approval list up front:** anything hard to undo — schema, key layout, storage/materialization format. Claude stops there with options and a recommendation.
- **Ship fixes behind runtime flags**, so the launch-week response to pressure is flipping a flag, not writing code.
- **Shape:** one coordinator session handing work to sub-agents (~11 at a time, 30 at peak). If that burns too many tokens per hour, a single agent works too.

### Make the system legible to Claude

Claude hill-climbs best on a clean signal: every number it measures should trace back to code you wrote.

- **Telemetry on every operation**, e.g. each DB query reports its name and rows scanned vs. rows returned — enough to spot and rewrite a bad query.
- **Claude adds the telemetry that's missing each iteration** rather than after something breaks.
- **Expect wrong first guesses, and let the next run kill them.** A 3 GB doc: shrinking a cache did nothing (the memory was in a dependency's own cache) so the change was dropped; finer-grained profiling found every keystroke copying the doc into several structures; copy-on-write took it to ~180 MB in ~3 days and cut the pod estimate from 500+ to ~50.
- **Lean the stack toward measurability.** They chose Rust (no GC shifting memory and latency on its own schedule) and minimal dependencies, vendoring the few they kept so they could be read and measured. This was a bet, not a bake-off against Go. "Hard for people to write" matters much less when Claude writes it.

### Cost

~$125k of Fable 5.2 list-price inference for the launch-scale push (author's estimate: about half was avoidable process experimentation). Author's untested estimate for a small stack (a couple of Kubernetes nodes + Postgres): $3k–$10k for two weeks. Spend went to reading telemetry, proposals, fixes and review.
