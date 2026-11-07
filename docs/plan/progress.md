# Progress

## 2026-11-07
- Created plan structure
- Problem defined: open, more accurate alternative to Surfline built on free data
- Scope: Orange County first; v1 spots listed in stage 02
- Stack decided: Python 3.14, uv, FastAPI, HTMX. Orchestrator leaning LangGraph.
- Model approach: hosted LLM plus retrieval of past observed days; no self hosting or fine tuning
- Logging flow: morning beach check plus optional post session follow up (stage 06)
- Next: answer open questions in vision.md, start stage 01 (uv init, first fetcher)
- Project set up on `feature/data-sources`: uv, Python 3.14, FastAPI, httpx, ruff, mypy, pytest
- Open-Meteo Marine fetcher built with offline tests; `GET /marine` returns the hourly forecast (defaults to HB Pier)
- Fixture is hand written in the documented shape; replace with a real capture (see tests/fixtures/README.md)
- Next: run against live data, then NDBC buoy fetcher
- Decided deployment: AWS (ECS Fargate, EventBridge, RDS Postgres, Secrets Manager), Terraform, Postgres in Docker locally (decision 0003)
- Budget set at under $50 to $60 a month; cheaper AWS design and Kubernetes local only (stage 08). Deployment not needed yet.
- Load balancer deferred (stage 08); AWS estimate now about $30 to $40 a month
- Database layer added: SQLAlchemy (async), Alembic, psycopg; `marine_snapshots` table stores every fetched forecast as JSON; Postgres tests run when DATABASE_URL is set
- Next: run Postgres locally and migrate, then NDBC buoy fetcher
- NDBC buoy fetcher added, defaulting to Long Beach Channel (NDBC 46256 / CDIP 215); `GET /buoy` shows recent readings. HB Nearshore buoy (46230) appears retired.
- Confirmed Long Beach Channel (NDBC 46256) as the primary buoy for Huntington Beach spots
- NWS hourly wind fetcher added on `feature/wind`; `GET /wind` returns 7 days of hourly wind (knots, direction) and air temp for HB Pier. Tide notes added to stage 02. Next: CO-OPS tides.
- CO-OPS tide fetcher added; `GET /tides` returns high and low tides (or hourly) for Newport Beach. Wind rules added to stage 02 (per spot shore angle, onshore 8 kt+ hurts, offshore and Santa Anas good). All four stage 01 sources done.
