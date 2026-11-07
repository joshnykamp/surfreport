# 05 Frontend

**Status:** Not started

## Goal
A simple web UI showing spots, today's prediction, the 7 day outlook, and the daily observation log.

## Approach
HTMX with server rendered templates (Jinja2) from FastAPI. No separate JS build. Revisit Next.js or similar only if the UI outgrows this.

## Acceptance criteria
- [ ] Spot list with today's score
- [ ] Spot page with height range, period, direction, wind, tide, water temperature and explanation
- [ ] 7 day outlook view
- [ ] Observation log form usable on a phone in under 30 seconds (see stage 06)

## Open questions
- Any CSS approach preference (plain CSS, Pico, Tailwind)?
