# Large multi-agent teams

Source: "Safely scaling multi-agent teams with Claude Fable 5.2" (Nov 2026). Toy experiment: 1,000 agents (1 lead + 999 helpers) reproduced a Lean formalization of Fermat's Last Theorem in 28.7 h, ⅓ the output tokens and ⅐ the length of the earlier 11-day, 6B-token run that needed a purpose-built platform and a researcher.

## Harness: general tools beat a bespoke platform

- Per agent: shell + file editor, its own sandbox (lightweight VM, no network), toolchain baked into the image, own Git branch + merge requests into main, shared Postgres via shell.
- One shared machine broke at ~100 agents (>half of runs OOM/disk/CPU) — use a VM per agent.
- SQL for coordination: general primitives, transactions handle concurrent writes, Claude knows it. No messaging tools; agents coordinate only via DB + Git.
- Prompt: task list with one-line descriptions, tool descriptions, a hierarchy (lead splits and assigns; helpers expect work, ask lead if unclear). No other guidance — the lead built five tables in 10 min: announce (orders), assign, notes (claims/progress), subtasks (anyone adds, first claimer owns), landed (finished log).
- Harness sent the lead periodic time-remaining reminders (19) to keep it going.
- A separate job merges to main (refuses only on conflict/fault); a grader checks results.

## Emergent behavior worth designing for

- Lead first has every helper judge difficulty; 47/60 statements were judged infeasible, then most were proved. **Agents misjudge difficulty and give up early** — human/lead encouragement helps; revisit "infeasible" verdicts when throughput exceeds assumptions.
- Control shifts from top-down assignment to helpers self-claiming from the subtasks table ("do not wait for me").
- Huge item → task tree (2,418 tasks, 10 levels): any helper splits a too-big piece into children; parents may assume children, so hundreds work in parallel.
- Domain platforms still help (faster compiles, reuse of human results); this isn't a case against them.

## Safety layers (no single layer suffices)

- **Sandbox**: no network, only a pipe to a gateway that calls the API and relays Git/SQL; gateway stamps agent identity outside the sandbox (no impersonation); push own branch only; DB unprivileged role, 5 s statement limit, writes refused >256 MiB; hardened kernel (no modules/kexec/raw memory/probes, lockdown); unprivileged user, no sudo, tools can't read/modify the agent loop; no credentials in sandbox.
- **Real-time**: prompted LLM classifier blocks each tool call, fail-closed; a block stops the whole team until a human reviews (a helper block removes only that helper; a lead block ends the run). Red-team (decomposition attacks) showed monitors that see CoT + inter-agent communication caught all sabotage attempts → run one, plus an action-only monitor in parallel so reasoning can't talk the monitor into allowing something.
- **Offline**: monitor over run records kept outside sandboxes, with extra affordances (can look up other agents' actions); escalates to run owners.
- Design monitoring assuming the model may be misaligned (experimental models skip pre-release alignment assessment).
