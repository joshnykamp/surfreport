# 0001 Agent orchestrator

**Status:** Proposed
**Date:** 2026-11-07

## Context
Need parallel data gathering from several sources plus an LLM synthesis step per spot.

## Options
- **LangGraph:** explicit graph with state, native fan out / fan in, checkpointing, good for deterministic workflows with LLM steps.
- **CrewAI:** role based agents that collaborate; quicker to start, less control over flow.
- **Plain Python (asyncio):** simplest, fewest dependencies, but no built in state, retries or tracing.

## Leaning
LangGraph. The workflow is a fixed pipeline with one reasoning step, which suits an explicit graph better than a crew of role playing agents.

## Decision
TBD
