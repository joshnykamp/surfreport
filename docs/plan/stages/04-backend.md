# 04 Backend and scheduler

**Status:** Not started

## Goal
Run the graph on a schedule, store reports, and serve them over an API.

## In scope
- API (FastAPI)
- Scheduler: every 6 hours or daily at midnight
- Postgres for reports and run inputs (Docker locally, RDS in AWS), SQLAlchemy and Alembic

## Acceptance criteria
- [ ] `GET /spots` and `GET /spots/{id}/report` return the latest report
- [ ] Scheduled refresh runs for all spots and logs failures
- [ ] Reports are stored historically, not overwritten

## Open questions
- Hosting: AWS ECS Fargate (see decision 0003)
- Scheduler: EventBridge Scheduler in AWS; how to run it locally?
