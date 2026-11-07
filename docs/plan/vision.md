# Vision

## Problem
Surfline is the default surf forecast, but its model is often inaccurate for specific breaks and it keeps getting more expensive. Meanwhile the underlying data (buoys, swell models like WaveWatch III, wind, tides, water temperature) is free and public. What's missing is an open tool that turns that data into an honest answer to one question: should I paddle out?

## Goal
An open source surf forecast that gathers free data sources and uses an LLM to translate them into a spot level prediction for the next 7 days, then improves from daily observations logged by surfers.

## Starting scope
- **Region:** Orange County, California. Small, well instrumented, and easy to verify against what's actually breaking.
- **Later:** The rest of California, then possibly worldwide.

## What determines "go or don't go"
- Swell height, period (16s beats 8s at the same size) and direction
- Swell shadowing by Catalina and the Channel Islands
- Wind speed and direction (offshore vs onshore)
- Tide height and direction
- Water temperature
- How each spot reacts to all of the above (see stage 02)

## Output per spot, per day
- Estimated surf height range (e.g. 2 to 4 ft)
- Swell period and direction
- Wind, tide and water temperature context
- Go / no go score with a short explanation

## How we know it works
- Every prediction is saved with the data it was made from.
- Surfers log what they actually see each morning (see stage 06).
- Accuracy is measured by spot and by days ahead.

## Model approach
- Use a hosted LLM; no self hosting or fine tuning for now. A year of daily logs is far too few examples to train on.
- Observations improve the system around the model: they tune spot config, and similar past days with their observed results are retrieved into each prediction prompt.
- Keep the model provider pluggable so self hosting stays an option if API costs grow.

## Success criteria
- [ ] A 7 day prediction for at least one Orange County spot, generated from live data
- [ ] Predictions refresh on a schedule without manual work
- [ ] Each prediction can be compared to an observed result
- [ ] Repo is public, documented, and runnable with `uv sync` plus one command

## Non goals (for now)
- Areas outside Orange County
- User accounts
- Paid data sources
- Training or hosting a custom model

## Open questions
- What time of day does a "day" prediction mean: dawn patrol, best window, or the whole day?
- Score scale: binary go / no go, 1 to 5, or both?
- License: MIT?
