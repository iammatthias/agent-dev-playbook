# agent-dev-playbook

A Claude skill distilled from the [claude.dev blog](https://claude.dev/blog/): Anthropic's own practices for building with Claude and Claude Code.

- `agent-dev-playbook/`: the skill (`SKILL.md`, topic files in `references/`, `sources.md`). Copy this folder into `~/.claude/skills/` or a project's `.claude/skills/`.
- `REFRESH.md`: how the corpus is updated. A Claude Code Routine runs it daily, and new posts are distilled and pushed to `main`.
- `scripts/check_sitemap.py`: diffs the claude.dev sitemap against `.sitemap/seen.txt` and downloads new posts.
