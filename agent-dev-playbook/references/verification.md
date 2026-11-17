# Verification loops for agent-written code

Source: "How the Claude Code team thinks about verification" (Nov 2026). Review layers, risk tiers and round caps live in `code-review.md`; this file is what the agent runs and how the checks themselves are kept honest.

Stance: verification is what lets you run dozens–hundreds of Claudes instead of 1–2 you check by hand. Tests, benchmarks and specs are now cheap to ask an agent for, and once written they run as software (few extra tokens). A separate grader checking output against a rubric: up to +10 pts task success vs. a plain prompting loop, most on the hardest tasks. Your job shifts from reading diffs to defining "done" and reading the evidence.

## Which tests to invest in

Avoid first: **flaky** tests train the agent to rerun instead of fix; **slow** tests get run less often and across bigger batches, so failures are hard to pin. Run heavy tests before commit, not after.

- **End-to-end — pick this if only one.** Real user flows (add to cart → checkout → confirmation). Hard to fool, definitive done criteria, and the failure says what broke (step trace + screenshot vs. a unit test's "Timeout after 30s"). Unit tests are faster and less flaky but can pass with the feature broken. Give the agent hands and eyes on the running system: a skill that boots, drives and inspects the app (CDP, simulators, API harness). A feature map (features from the user's view: paths, shortcuts, selectors, expected results) doubles as guide and grading rubric.
- **Property tests.** State something that can't fail; let fast-check (JS/TS), Hypothesis (Python) or proptest (Rust) generate thousands of inputs against it. Edge cases without the authoring agent's bias. Useful properties: round-trip (encode→decode, parse→serialize), invariants ("balance never negative"), idempotency (migration, normalization, retry twice = once), equivalence (optimized = naive-but-correct). Especially good for rewrites where the spec has drifted from production behavior.
- **Differential tests.** For migrations expected to preserve behavior: same inputs through old and new, any diff is a bug or breaking change. Use random inputs or sampled production traffic, normalize noise (whitespace), keep an allowlist of approved differences.

## Running the change

- Running the app end to end matters more than tests. Chrome extension for web, iOS/Android MCP for mobile, computer use for desktop, run the service locally for backend.
- Codify how to start/drive the app as a skill named **`verify`** in `.claude/skills/`, placed as close to the relevant code as possible; as many as needed. Claude uses it before committing. It's the smoke-test harness: have Claude iterate on and stress-test it until it's fast and reliable.
- **Cheap checks first.** Tests, build, linter before opening a PR so shared review/CI time isn't spent on locally catchable bugs. Enforce with a hook that runs tests when Claude finishes, or a `/goal` of a passing suite.
- **Failures route humans.** Claude runs checks and fixes failures; still failing after 3 rounds → stop and bring in a person.
- **Flaky tests:** no skipping, added sleeps or retry-until-green. If no root cause is found, delete the test and write down why.

## Designing the checks

- **Owners write them** and refine until the check flags what the owner would. A check that pulls in a reviewer says why, so they don't reconstruct it from the diff.
- **Diff-triggered reliability checklist.** 39 items, each = a trigger readable from a diff + a check + the incidents/PRs behind it (e.g. session storage or message types change → does a new field load safely when `--resume` reads old transcripts without it?). Claude checks only items whose trigger matches, usually 3–10.
- **One reviewer, tuned** (`REVIEW.md`) beats stacking a second, pricier reviewer on top.
- **Rounds build on each other:** point each pass at earlier rounds' context and past failures instead of re-checking from scratch. Cheaper and finds more.

## Keeping checks honest

- **A change can't modify its own judge.** Gating rules live on a branch the change can't touch; Code Review reads `REVIEW.md` from the base/default branch, never the PR.
- **A review is for one commit.** A pass on a commit that's since been pushed over means nothing.
- **Stamp every commit with how it was verified**, including `none`, so unverified commits are queryable.
- **Roll out a new gate as off → observe → enforce.** Example: block commits whose session had no `/code-review` or `/verify`. Observe logs what would have been blocked; review false positives before enforcing. In enforce, a commit message can carry a reason for skipping, and after 2 blocks in a session the next commit passes so Claude can't get stuck.

## Grading the checks

- Track: merged changes later reverted, changes a maintainer rejected before merge, and a size-matched set that stayed clean.
- Formal eval (extends `code-review.md` "Incidents → eval"): rebuild the repo at review time per past incident/revert, one-sentence answer key, points only for findings that describe that bug; merged-and-stable changes as the over-flagging control; tuning set split from a fixed test set.
- Measure recall separately for raw findings, post-verification and the final review; one end-to-end score hides where found bugs get dropped.
- Score importance as well as validity (must-fix / should-fix / nit; Important / Nit / Pre-existing, where Pre-existing isn't the author's fault).
- Tune recall only until the next gain would be overfitting the eval.

## Misses → rules

- **Mined:** patterns from human review comments and reverts; must appear in ≥2 PRs and be identifiable from a diff; 3 agents try to disprove each; a human approves it in a PR.
- **Replayed:** run 3 bug finders on a PR tied to a known incident. ≥2 find it → detectable. Missed on a small diff → a gap worth a `REVIEW.md` rule.
- A repeated failure (e.g. logging user data) becomes a hook or explicit `CLAUDE.md` rule.
- **Prune on a routine:** test suites, verification steps and `.md` rules only grow unless tidied.
