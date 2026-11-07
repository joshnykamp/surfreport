# 0002 Backend and frontend stack

**Status:** Decided
**Date:** 2026-11-07

## Decided
- **Backend language:** Python 3.14
- **Package and env management:** uv
- **API:** FastAPI
- **Models and validation:** pydantic
- **Frontend:** HTMX with Jinja2 templates served by FastAPI. Chosen for simplicity: one app, no JS build. Swap to Next.js or similar only if the UI outgrows it.
- **Quality gates:** ruff, mypy, pytest (see AGENTS.md)

## Proposed
- **Storage:** Postgres (see 0003)
