# AGENTS.md

This repository is a set of Claude Code skills and prompts. It is meant to be readable by both humans and agents.

## For agents

1. Read `manifest.json` first. It lists every skill and prompt with a `path` and a `raw` URL.
2. Each skill is self-contained under `skills/<name>/`; the entry point is `SKILL.md`.
3. To install locally, copy the skill directory into `~/.claude/skills/`. The directory name is the skill name.
4. Paths such as `~/My_Skills/` are **defaults**, not hard requirements. Ask the user or use their configured location.
5. Do not modify files outside the skill you were asked to use.
6. Skills are instruction files, not executable code. `ocr-vision` and `bili-learn` may call external tools or APIs; confirm before spending the user's quota.

## For phone clients

- If the client can enumerate JSON, fetch `manifest.json`.
- If it can only fetch one file at a time, fetch the needed `SKILL.md` directly.
- Raw base: `https://raw.githubusercontent.com/la1379/ai-toolkit/main/`

## Licensing

- Scripts/code: MIT (`LICENSE`).
- Skill and prompt text: CC BY 4.0 (`LICENSE-prompts`).
