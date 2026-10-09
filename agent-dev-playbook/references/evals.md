# Evals and hillclimbing

Source: "Automating eval design and hillclimbing with Claude" (Sep 2026). Commands: `/claude-api build-eval`, `/claude-api hillclimb` (run `claude update` first).

## Four properties of a good eval

1. **Tasks mirror production.** Not what's easy to generate or grade.
2. **Scores rise with stronger models and more effort.** If not, suspect ambiguous tasks or a bad grader.
3. **Passable headroom.** Best model at max effort well below 100%, but not from impossible tasks (tell: a task that fails every replicate). Two experts should agree on the verdict; everything graded is stated in the task.
4. **Low run-to-run variance.** Watch grader nondeterminism, inconsistent config (effort), and leftover environment state that leaks answers.

**Avoid adversarial sampling:** choosing cases because today's model fails them measures that model's failure fingerprint. Pick cases a human can explain as hard. Sources in order: production transcripts (check retention/sensitivity), bug reports/tickets, 5–10 handwritten, then synthetic anchored on real ones. Raw user traffic can skew easy.

## Grader

- Cheapest that fits: programmatic (exact match, fixed label set, schema, tests) when output is constrained.
- LLM-as-judge for open-ended output: rubric of **checkable claims**, not a 1–5 scale. With a baseline, pairwise in random order, blind to which is baseline. Judge ≠ model under test.
- Read graded transcripts before trusting the grader; have humans re-grade a handful.
- Diagnostics: grade the same output twice (verdict stable?), check timeouts/API errors/truncation, warn if baseline ≥ ~95% (climb cost/latency instead).
- Output: cases, grader, runner, one JSON line + transcript per case, simple local results page, score with confidence interval.

## Hillclimbing

Good targets are **cheap to iterate** (prompts, skills, tool descriptions, model/effort), **attributable** (e.g. skill description ↔ trigger rate), and **well-scoped**. Cost-at-parity is a strong objective even on saturated evals.

**Anti-overfitting**
- Random train/test split; climber only reads train. Train ↑ with test flat ⇒ revert.
- Never paste failing cases into the prompt.
- Keep answers structurally unreachable (no public repo with solutions, no curl-able references).
- Watch harness leaks: adding tools/rules that only help eval-specific traits (OCR tool, hardcoded paths, tuned phrasings, one patch per failure).

**Loop**
1. Choose goal (performance, or cost holding performance) and editable surfaces.
2. Check eval noise < smallest gain you'd act on; else add reps/cases.
3. Each round: read train transcripts, propose **one** root-cause patch big enough to show above noise; keep only if train and test both improve; revert regressions.
4. On a 2–3 round stall: make no edit — bucket every remaining failure by cause. Reveals ambiguous tasks, broken graders, harness errors, or model priors (e.g. old API shapes — fix with a "you remember X → current is Y" table near the top).
5. Finish on best test-set version; report vs baseline with CIs; if within noise, don't merge.

**Results seen:** support benchmark Opus 4.8 high (74.4%, 4.6¢) → audited prompt + Opus 5.5 low (87.8%, 1.9¢) → Sonnet 5 low (88.9%, ~1¢) → improved prompt (98.9%); held-out 78.6% → 90.5% at ~1/5 cost. claude-api skill 66% → ~88% by filling coverage gaps, fixing type tables, adding prior-correction table, fixing broken graders.
