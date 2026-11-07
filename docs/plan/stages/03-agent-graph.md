# 03 Agent graph

**Status:** Not started

## Goal
An agent workflow that gathers data in parallel and produces a structured report per spot.

## Proposed shape
```
            ┌─ buoy node ─┐
spot ──────►├─ wind node ─┤──► synthesis agent ──► report (structured)
            ├─ tide node ─┤
            └─ swell fcst ┘
```
- Fetch nodes call stage 01 fetchers (fan out, run in parallel)
- A retrieval step adds similar past days and their observed results (stage 06)
- Synthesis agent (hosted LLM) gets the spot model, data and past days, returns a structured report
- Output validated against a pydantic schema

## Acceptance criteria
- [ ] Graph runs end to end for one spot from the CLI
- [ ] Fetch nodes run in parallel
- [ ] Report output is schema validated (height range, period, direction, score, explanation)
- [ ] Every run saves its inputs and output (needed for stage 06)
- [ ] LLM provider is configurable

## Open questions
- LangGraph or CrewAI (see decision 0001)
- Which LLM, and what is the cost per spot per refresh?
- Should the LLM produce the score, or explain a score computed in code?
