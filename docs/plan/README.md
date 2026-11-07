# Plan Index

**Goal:** An open source alternative to Surfline. Gather free buoy, weather and ocean data and have an LLM predict surf for Orange County spots over the next 7 days: size range, period, and a go / no go score. Predictions are checked against daily observations from surfers.

**Current stage:** 01 Data sources (branch `feature/data-sources`)

## Status

| Stage | Status | Link |
|---|---|---|
| 00 Vision | Draft | [vision.md](vision.md) |
| 01 Data sources | In progress | [stages/01-data-sources.md](stages/01-data-sources.md) |
| 02 Spot model | Not started | [stages/02-spot-model.md](stages/02-spot-model.md) |
| 03 Agent graph | Not started | [stages/03-agent-graph.md](stages/03-agent-graph.md) |
| 04 Backend and scheduler | Not started | [stages/04-backend.md](stages/04-backend.md) |
| 05 Frontend | Not started | [stages/05-frontend.md](stages/05-frontend.md) |
| 06 Feedback loop | Not started | [stages/06-feedback.md](stages/06-feedback.md) |
| 07 Wearable data | Idea | [stages/07-wearables.md](stages/07-wearables.md) |
| 08 AWS deployment | Not started | [stages/08-aws-deployment.md](stages/08-aws-deployment.md) |

## Decisions

| # | Decision | Status |
|---|---|---|
| 0001 | [Agent orchestrator](decisions/0001-orchestrator.md) | Proposed |
| 0002 | [Backend and frontend stack](decisions/0002-stack.md) | Decided |
| 0003 | [Deployment, infrastructure and database](decisions/0003-deployment.md) | Decided |

## Other
- [progress.md](progress.md): session log
- [stages/_template.md](stages/_template.md): template for new stages
