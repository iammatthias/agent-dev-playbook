# Claude Code mods

Source: "Getting started with Claude Code mods" (Oct 2026). Requires Claude Code ≥ 2.1.287. API may change between releases — the types Claude Code writes into `.claude-plugin/types/` on load are authoritative. Built-in `plugin-authoring` skill / just describe the mod to Claude.

A mod is a plugin whose behavior is a JS/TS module of in-process hooks that can observe, rewrite, or answer session events and draw UI (terminal and desktop). Unlike settings hooks (shell command per event, JSON over stdio), a mod loads once, keeps state, draws live UI, and calls back into Claude Code. Claude Code's own AGENTS.md support and `/diff` pane are mods (`anthropics/claude-code` → `mods/`).

## Shape

```
my-mod/
├── .claude-plugin/plugin.json   # manifest; add "types": "./types/index.d.ts"
├── hooks/hooks.json             # { "modules": ["./my-mod.mjs"] }  (exactly one)
├── hooks/my-mod.mjs             # export function register(on, options)
├── types/index.d.ts             # declares PluginState keys
└── tests/my-mod.test.ts
```

```js
on("tool.call", { tool: "Bash" }, async ($, e, next) => next(e));
```
`$` = API (ui, session, state, store, fs, process, clock, http, tool, command, model…). Hooks chain like middleware:
- **Observe**: `const r = await next(e); …; return r`
- **Rewrite**: `return next({ ...e, command: safer })`
- **Answer**: return `{ deny: "…" }` (or a result) without `next`

Events: `tool.call`, `prompt.submit`, `turn.start`/`turn.complete`, `session.start`/end, `command.run`, `ui.render` (per component, e.g. `AbovePrompt`, `Pane`). Sandbox: no DOM, no Node — everything goes through `$`.

## Habits

- **State in `$.state`, not module variables** — every save hot-reloads and reruns `register`/`session.start`. Declare keys in `types/index.d.ts` under `interface PluginState`, or `claude plugin validate` fails. `$.state.get` inside a render subscribes it → automatic redraw on `set`.
- **Props live on `e.props`** (`hasSurvey`, `bodyColumns`…). Size to `bodyColumns`; yield with `next(e)` when there's nothing to draw or a survey wants the slot.
- Element constructors come from `$.ui.resolve(e)` (per surface); JSX works with `h`.
- Use single-width symbols, not emoji.
- Filter subagent turns with `e.agentId`.
- `$.session.usage()` gives context tokens/window/percent cheaply.
- `$.process.run([...argv])` for dry runs (no shell injection). Waiting inside `$` calls doesn't count against the 10 s per-dispatch hook budget; honor `next.signal.aborted`.
- `$.ui.open({id,title,focus})` → if `isPlaced: false`, degrade to the `AbovePrompt` band.
- `Button({ label, hotkey, onPress })`; `$.command.register` in `session.start`, answer on `command.run`; `$.ui.status`, `$.ui.toast`.
- Command-text guards are a safety net, not a permission system — use permission rules for hard blocks.

## Dev loop

- `claude --plugin-dir ./my-mod` (folder watched, hot reload).
- `claude plugin validate ./my-mod` — reports hooks, calls, state reads/writes.
- `claude plugin test ./my-mod` — `claude-code/testing`; hooks registered in tests run after the mod and stub Claude Code's answers; `$.ui.mount` + `ui.find`.
- `claude --debug` when a render doesn't show (invalid tree).
- Share via a marketplace (`.claude-plugin/marketplace.json`), `/plugin marketplace add org/repo`, `/plugin install name@market`, `/reload-plugins`. Mods run with Claude Code's access — install only from trusted publishers.

Ideas: cost/rate-limit meter, prompt.submit convention injector, files-read map pane, long-turn toast, stack-specific `tool.call` guard (prod kubectl, `terraform apply`).
