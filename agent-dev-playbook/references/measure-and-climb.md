# Measure-and-climb loop (performance and beyond)

Source: "How we made claude.ai 3x faster in two weeks" (Sep 2026). 13 journey measurements, 3.1× geomean faster, 3,000+ changes, zero customer incidents or rollbacks.

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
