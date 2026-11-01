# IDEAForge agent instructions

## Product
IDEAForge helps one person turn a technical idea and supplied references into a testable prototype plan in a Switch room.

## Non-negotiable rules
- Preserve the user's original idea wording.
- Label claims `SOURCE_BACKED`, `INFERENCE`, `ASSUMPTION`, or `UNKNOWN`.
- A source-backed claim needs an existing source ID and exact locator. Never invent evidence.
- Ask at most two high-value questions at a time.
- The lead delegates visibly to the named specialists and reconciles conflicts in the room.
- Ask the human to confirm scope before prototype planning.
- The dossier stays draft until the human explicitly approves it.
- Never make legal conclusions about novelty, patents, infringement, or filing readiness.
- Never purchase, control hardware, run arbitrary scripts, or perform external actions.
- Keep local sources and credentials private; use only authorized room materials.

## Build and verify
- Keep Switch collaboration visible; use the CLI only for deterministic local ingestion, validation, and rendering.
- Use `python -m ideaforge --help` for current command syntax.
- Run `python -m pytest`, `python -m ruff check src tests`, and `python -m ruff format --check src tests` after code changes.
- Never claim the Switch room was tested unless it was tested in Console and Mattermost.

## Current project references
- Product and scope: `SPEC.md`
- Switch room setup: `docs/SWITCH_SETUP.md`
- Demo: `docs/DEMO_SCRIPT.md`
- Security: `docs/SECURITY_AND_PRIVACY.md`
