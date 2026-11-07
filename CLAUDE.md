# Surf Report

Open source surf forecast for Orange County. Python backend (uv, FastAPI), HTMX frontend, and an LLM agent workflow that combines buoy, swell, wind, tide and water temperature data into a 7 day per spot prediction with a go / no go score.

Project setup, conventions and quality gates live in AGENTS.md:

@AGENTS.md

## Before starting any work
1. Read `docs/plan/README.md` for current stage and status.
2. Read the stage file you are working on in `docs/plan/stages/`.
3. Check `docs/plan/decisions/` before proposing a change to something already decided.

## When ending a session
Update `docs/plan/progress.md` with what was done, what is next, and any open questions.

## Project specific rules
- Keep data fetchers deterministic and testable; agents consume their output.
- Never commit API keys. Use `.env` (gitignored) and `.env.example`.
