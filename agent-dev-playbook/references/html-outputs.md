# HTML instead of Markdown for outputs

Source: "Using Claude Code: The unreasonable effectiveness of HTML" (May 2026). Gallery/templates: thariqs.github.io/html-effectiveness, github.com/anthropics/html-effectiveness.

People stop reading Markdown past ~100 lines, and it's hard to share. HTML carries tables, CSS design, SVG diagrams, code, interaction, spatial layout, and images — and renders anywhere via a link. It also keeps you *in the loop* with long-running work. Token overhead is negligible at 1M context.

Just ask: "make an HTML file / artifact." Know what you want it to do; build a skill once patterns recur.

## Use cases

- **Specs, planning, exploration** — a web of HTML files: options side by side with tradeoffs → mockups of the chosen one → implementation plan with data flow and key snippets. Pass all of them to a fresh implementation session and to the verifier.
  - "Generate 6 distinctly different approaches — vary layout, tone, density — in one HTML grid, label each with its tradeoff."
- **Code review/understanding** — rendered diff with severity-tagged margin annotations; flowcharts of unfamiliar modules; PR explainers.
- **Design & prototypes** — design in HTML even if the target is React/Swift; sliders/knobs for animation or tokens; "copy parameters" button.
- **Reports, research, learning** — explainers with diagram, annotated snippets, gotchas; status/incident reports; decks. Feed from Slack/git/codebase/MCPs.
- **Throwaway custom editors** — purpose-built single-file UI for one dataset (drag tickets across Now/Next/Later/Cut; form editor for flags with dependency warnings; prompt template editor with live previews). **Always end with an export**: "copy as JSON/prompt/diff/Markdown" to paste back into Claude Code.

Good for: reordering/triage, structured config editing, tuning prompts with preview, dataset curation, annotation, values hard to type (colors, easing curves, crops, cron, regex).
