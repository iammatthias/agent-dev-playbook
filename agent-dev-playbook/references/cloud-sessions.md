# Claude Code cloud sessions

Source: "Claude Code in the cloud: a field guide to cloud sessions" (Oct 2026).

A cloud session = Claude Code on its own fresh VM (~4 vCPU, 16 GB RAM, 30 GB disk), repo cloned onto a new `claude/` branch, environment setup done. Ends with a branch, then a PR if wanted. No separate compute charge; draws on plan limits (N parallel sessions burn limits ~N× as fast). Not available via Console API key or third-party providers; ZDR orgs have it off.

## Local vs cloud

- Cloud wins: parallel tasks (no shared tree/ports), laptop asleep/offline, long proof loops, untrusted code (disposable VM, no SSH keys/`~/.claude`, narrowable network).
- Stay local: local-only data/VPN/GPU/simulators/hardware, tight visual loops, ZDR orgs.
- Cloud approval modes: Auto, Accept edits, Plan only (no per-command).
- Between: remote control (session stays on your machine, steer from phone); self-hosted environments (beta, Team/Enterprise, reach private networks).

## Commands

```
claude --cloud "<self-contained task>"        # push local commits first: VM clones from GitHub
claude --permission-mode plan                 # plan locally, commit plan, then --cloud "Execute docs/plan.md"
claude --teleport [<id>]  (/teleport, /tp)    # pull session branch + conversation into terminal; needs clean tree, pushed branch
claude -p "rebase on main and push" --cloud <session-id>   # queue follow-up from anywhere, incl. CI
/autofix-pr                                   # watch PR: fixes CI failures and review comments
/schedule                                     # routines (research preview; also claude.ai/code/routines)
/web-setup                                    # send `gh` token to your account (no App needed, but no auto-fix/triggers)
```

Prefilled session URL: `claude.ai/code?prompt=...&repositories=org/repo`.

## Working patterns

- **One task, one session**, written as a ticket: what's wrong, what done looks like, the command that proves it ("run the suite 30 times in a row"). Ask for evidence and read the summary before the diff.
- **Split parallel tasks along file boundaries**; sessions can't see each other's fixes and may report a bug another is fixing. Merge in order, then send follow-up "rebase on main" to the next.
- **Ask for heavy proof**: 200 suite runs, bisect 50 commits, slow integration tier, start the app and curl it. Long runs inside one command are cheap in turns.
- Foreground commands time out at 2 min (max 10), then run in background up to 30 more; raise via `BASH_DEFAULT_TIMEOUT_MS` / `BASH_MAX_TIMEOUT_MS`.
- Commit as you go: idle VMs are reclaimed (reopen = fresh VM, conversation restored).
- Auto-fix doesn't hear about base-branch merge conflicts: ask for a rebase. Reply threads post under your username.
- Routines: no approval prompts, push to `claude/` branches by default; triggers = schedule (hourly min), HTTP endpoint, GitHub event.
- Team/Enterprise: set session visibility to Team; commits carry a `Claude-Session` trailer linking the transcript.

## Environment setup (so it can check its own work)

- Start with Default env (Trusted network: registries, GitHub, cloud SDK hosts). Narrowest network that works; None for strictest (API traffic and own-branch push still possible). Changes apply to running sessions in ~1 min.
- **Setup script**: runs as root before Claude Code; must exit 0; keep under ~5 min so the snapshot caches (rebuilds on script/host change and ~7 days). Cache holds files, not processes: start services (`service postgresql start`) per session.
- **SessionStart hook** in repo `.claude/settings.json` for `npm install` etc. (same locally and cloud); gate with `CLAUDE_CODE_REMOTE`.
- Env vars are visible to everyone using the environment; use the environment's API credentials (key attached outside the VM per host) instead of secret vars.
- Only repo config travels (`CLAUDE.md`, rules, skills, agents, commands, `.mcp.json`); `~/.claude` doesn't. Put test commands in CLAUDE.md.
- GitHub token never enters the VM: a proxy holds it; session gets a short-lived credential that pushes only to its own branch.

## Connecting GitHub

Two separate permissions: sign-in (identity; public repos only) and the Claude GitHub App installed on the account/org that owns the private repo (also required for auto-fix, GitHub triggers, projects).

| Symptom | Fix |
|---|---|
| Private repo missing | Install App on owning account/org, or add repo to its access list |
| "must be an owner of the organization" | Owner accepts pending App permission request / IP-allowlist inheritance / SAML grant |
| Org repos missing after connect | SAML SSO step skipped: Authorize each org in GitHub settings, reconnect |
| Every session auth error | Org IP allowlist: ask support to exempt Anthropic-hosted services |

No-GitHub fallback: `claude --cloud` uploads a repo bundle (can't push back unless connection has push access). GitLab/Bitbucket: bundle only. Team/Enterprise: owner enables GitHub connector + cloud sessions in admin settings; optional Quick setup for `/web-setup`.
