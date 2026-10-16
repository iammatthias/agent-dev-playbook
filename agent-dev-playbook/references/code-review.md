# Code review at agent volume

Source: "How the Claude Code team does code review" (Oct 2026). Claude writes ~90% of Claude Code's code; Jun→Sep merged PRs more than doubled while revert share fell >40%.

Stance: "did a human read it?" is a proxy for "what could go wrong, and which check (automated or human) catches it?" Review runs continuously (like spellcheck), not as an end gate. Goal: most PRs merge with ≤1 human (can be the author) and no rise in reverts/incidents. Measure human approvals per PR (median/p95), human comments, wait time; revert + incident rate are the guardrail.

## Layers (each leaks; later ones catch the rest)

1. **Verify before the PR.** Give Claude something runnable (tests, build, screenshot vs. design) and ask for output, not "done"; then a fresh-context subagent reviews the diff. Skills for bug-hunt, simplify, end-to-end check. Verification ≈ 2–3× better results.
2. **AI review on every PR.** Reads diff against whole repo + stated intent; on bug fixes looks for root cause. `/code-review` locally, Code Review for Claude Code (Team/Enterprise; Quick/Standard/Deep per repo, Deep where a miss is costly). Substantive-comment share 16%→54% at launch.
   - Multiple agents hunt in parallel, a separate group votes on each finding, posted only if enough agree; style/diagnostic/cleanup-only findings dropped. Inline, tagged Important / Nit / Pre-existing.
   - Every finding gets fixed or resolved with a reason.
3. **Security review that blocks.** No merge with an open bug or security finding; fixed by a later commit clears itself. `/security-review` or the security-review Action.
4. **Required CI.** Lint, types, all-platform tests, build. PR template: how tested, **how to undo**, risk; the requester signs off.
5. **Human approval by risk.** Low (docs, copy, flagged additive) none once automated checks green; medium (product, caching, auto-updater, system prompts) one person; high two. The *change* sets the tier (classifier), not the author; second classifier can add a human. Owner-listed sensitive paths and CI workflow files always need a person. Lighter paths only for trusted authors. A bot approval never fills a human slot. Whoever prompted an agent PR counts as a required reviewer. Approval binds to one commit; unvouched pushes/hand-resolved merges re-require it.
6. **Merge queue + flags + staged release.** Queue re-runs checks on main+change; flag to employees first; `latest` before `stable`.
7. **Fast detection/rollback.** Flags off without deploy; on-call; incident reviews ask which layer should've caught it. No circuit breakers yet.

## Improving the reviewer

- **Fix repeat flags at the source:** skill, lint rule, `CLAUDE.md` (short, stack/conventions/non-goals; reviewer flags violations and stale lines), `REVIEW.md` (code-owner written: what failure looks like here, cap nits, paths to skip, require file+line evidence, summary opens with a count and says "nothing to fix" plainly). Test that the reviewer actually follows it.
- **Incidents → eval.** Past incident/revert PRs, expert-confirmed bug locations, reviewer scored daily; keep a reviewer change only if score rises. Rescore when prompts, tools or model change.
- **Measure noise** by response: fixed / wrong / intentional / don't care; also run on known-clean PRs. Priority: real bugs first, fewer rounds second. Noise costs more with agent authors (each nit = commit + round).
- **Force convergence.** One PR hit 50+ overnight rounds; ~59% of repeat flags were code present since pass one. Fixes: cap at 3 rounds (then ask author to rethink approach), diff-only re-review after first few, flag the bug *class* so all instances get fixed, no repeat findings. Result: pass-in-one-round 65→78%, ≥5 rounds 8.9→1.5%, mean reviews 2.08→1.32.
- Nightly review agents over existing code.

## Humans keep

Should we build this; risky code (billing, updater, CI); architecture others will copy; reading the evidence (test output, command, screenshot, findings; if unsure what checks miss, ask for real review); owning the outcome. Context-sharing: ask Claude for an explainer of the slice you're about to change (or a small teaching artifact) instead of reading trivial diffs. "You land it, you own it": small changes, reversible, blast radius sets the bar; raise direction changes early in thread, not as a blocking comment on a finished PR.

## Adopt

Short `CLAUDE.md` + format/lint hooks → local `/code-review`, `/security-review` → `REVIEW.md` → AI reviewer on one repo, tune weeks, widen → require resolved threads → written risk tiers (start strict) → CODEOWNERS/branch protection for auth, billing, CI, installers → dismiss approvals on new commits → merge queue, flags, rollback.
