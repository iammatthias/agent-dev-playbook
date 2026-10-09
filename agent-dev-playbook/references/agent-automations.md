# Scheduled agent automations

Source: "Building effective agent automations" (Oct 2026); reference impl `anthropics/claude-quickstarts/managed-agents/daily-brief` (Claude Managed Agents, beta). Walkthrough: `/claude-api managed-agents-onboard <post URL>`.

Shape: schedule wakes agent → reads named sources (read-only) → posts to one destination; memory holds state (agent-writable) and preferences (user-writable, agent read-only); guardrails around it. Config as files applied with `ant apply` (agent.md, deployment.md, environment.yaml, memory stores, vault.yaml; IDs in `claude-lock.json`). Manual test run: `ant beta:deployments run --deployment-id <id>`.

## Six rules

1. **Read from a bookmark, not a fixed window** ("last 24h" gaps on late runs, repeats on early). Store newest-item timestamp per source in `bookmarks.json` in the state memory store.
2. **A failed read is not a quiet day.** A down/expired MCP server just drops its tools silently. Rules: keep that source's bookmark, brief from the rest, end with a line naming what couldn't be read.
3. **Re-check every item right before posting** (live source). Resolved → drop; changed → fix; unconfirmable → drop and log in the run record. Assert status or drop it, never hedge. Copy links from the source's link field, never assemble them.
4. **Count a post as sent only on confirmation** (Slack `"ok": true` + message ts), then update ledger and bookmarks. Before posting, check the channel for today's title (no double posts). Unclear result → mark run "maybe posted", change nothing else. Run record `runs/<date>.md`: "posting" → "posted"/"maybe posted".
5. **Re-read preferences every run** from a store the agent can't edit; baked-in copies go stale. If unreadable, stop and say so, don't run on defaults. Agent proposes preference changes in its own state store.
6. **Least privilege + spend cap.** Read-only tokens wherever it only reads; network allowlist; invite the bot only to needed channels.

## Details

- Credentials in a vault, real values outside the sandbox: MCP calls go via a proxy matching the vault credential's URL; shell sees an opaque `$SLACK_BOT_TOKEN` swapped in at egress for allowed hosts. Prompt-injected text in sources can still skew the brief (incl. via saved notes) but can't write to GitHub or edit rules.
- Unattended = no approvals: MCP toolset needs `permission_policy: always_allow` (with read-only token); built-in bash runs without approval.
- Brevity rule in the prompt: an item earns a line only if the reader would act on it today or it changes a pending decision; when unsure leave out; counts aren't items; open ledger items carried as one line ("still waiting, day 3"); closed items dropped silently; don't revive retired topics.
- Ledger line = date, source, immutable ID (Slack ts / PR number), last status. Stale memory failure modes: reporting resolved items as waiting, dropping open ones as "already reported". Also keep per-source notes ("returns only newest 50").
- Dates: set `timezone` on the cron and tell the agent the zone in the first message, or "this morning" becomes "yesterday".
- Budget: start at 3–5× a normal run's cost, tighten from real numbers. A run at cap pauses (`budget_reached`), which looks like a brief that went quiet. `max_list_cost.amount` is a string in cents (`"500"` = $5).
