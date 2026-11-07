# 02 Spot model

**Status:** Not started

## Goal
Define what a spot is and how offshore swell translates into surf at that spot. This is the core local knowledge and the main advantage over generic forecasts.

## v1 spots (Orange County)
| Spot | Known behavior |
|---|---|
| HB Pier, northside | Usually good; often a bit better than southside |
| HB Pier, southside | Usually good |
| Bolsa Chica to the Cliffs | Beach break; usually a little smaller |
| Newport jetties | Each jetty breaks differently; named by street number (e.g. 56th St) |
| Blackies | Usually small |
| The Point (optional) | Between Blackies south side and the Wedge; gets big |

## Reference data
- Primary buoy for Huntington Beach spots: Long Beach Channel, NDBC 46256 / CDIP 215 (confirmed)

## Tide effects (local knowledge)
- High or deep tide: waves get sluggish or break right on the beach
- Low tide: waves get hollow and barrel, but at some spots can shut down or disappear
- Each spot needs its own good tide window

## Wind effects (local knowledge)
- Offshore vs onshore depends on each spot's shore facing direction, so every spot stores a shore normal angle and wind is judged relative to it
- From the HB Pier through Bolsa Chica the beach faces about southwest, so NE through E is offshore; the coastline starts to turn at Newport, so Newport spots need their own angle
- Onshore around 8 knots or more makes the waves crumble; still surfable, but quality drops
- Offshore is good, including strong Santa Ana winds

- Spot metadata: name, lat/lon, nearest buoys, tide station, facing direction, ideal swell direction window, ideal tide range, ideal wind direction
- Swell shadowing: which swell directions are blocked by Catalina and the Channel Islands per spot
- A per spot size adjustment relative to the buoy (e.g. "runs smaller than the buoy suggests"), tunable from observations
- Spot data stored as versioned config (YAML or JSON) in the repo

## Acceptance criteria
- [ ] All v1 spots defined in config
- [ ] Shadowing is represented per spot
- [ ] A baseline size estimate exists and is testable without an LLM
- [ ] Adding a new spot is a config change, not a code change

## Open questions
- Which Newport jetties (by street) to include in v1, and is each its own spot?
- Where does the baseline size formula come from?
