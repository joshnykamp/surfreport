# 01 Data sources

**Status:** In progress

## Goal
Deterministic Python fetchers that pull buoy, wind, tide and swell forecast data and return clean, typed objects. No agents here.

## Candidate sources (all free, verify terms before use)
| Data | Source | Notes |
|---|---|---|
| Buoy observations | NOAA NDBC | Real time wave height, period, direction |
| Buoy observations and swell forecast | CDIP (Scripps) | Strong California coverage |
| Swell forecast | Open-Meteo Marine API | Global, simple JSON, 7 day |
| Wind and weather | NWS API (api.weather.gov) | US only |
| Tides | NOAA CO-OPS | Predictions per station |

## In scope
- One fetcher module per source
- Shared typed models (pydantic) for observations and forecasts
- Caching raw responses for tests and replay

## Out of scope
- Interpreting the data (stage 02 and 03)

## Acceptance criteria
- [ ] Each fetcher returns a typed object for a given station or lat/lon
- [ ] Unit tests run offline against saved fixtures
- [ ] Failures (source down, missing fields) are handled and reported, not crashed on

## Tasks
- [x] `uv init`, set up project layout, ruff, mypy, pytest
- [ ] NDBC fetcher
- [x] Open-Meteo Marine fetcher (swell, waves, water temp)
- [ ] NWS wind fetcher
- [ ] CO-OPS tide fetcher
- [ ] Save fixtures

## Open questions
- Global expansion means NWS and CO-OPS will not cover everything. Lean on Open-Meteo for non US?
