# 06 Feedback loop

**Status:** Not started

## Goal
Capture what the surf actually looked like and use it to measure and improve predictions.

## Logging flow
1. **Morning check (from the beach, before paddling out):** open the app, see today's prediction, log what you see. Target: under 30 seconds.
   - Spot
   - Observed size range
   - Quality (e.g. poor / fair / good / great)
2. **After session (optional):** one tap: better, same, or worse than it looked from the beach.

## How observations are used
- Tune per spot config (e.g. size adjustment vs buoy)
- Retrieve similar past days with their observed results into the prediction prompt
- Measure accuracy by spot and by days ahead

## Acceptance criteria
- [ ] Each observation links to the stored prediction and its inputs
- [ ] Morning log works on a phone in under 30 seconds
- [ ] Optional post session follow up can be added to an existing observation
- [ ] An accuracy metric can be computed per spot over time
- [ ] Past observations can be replayed against a changed prompt or config (offline eval)

## Surf log (main source of observations)
Give surfers a personal surf log they want to keep for themselves. Because the log is for their own record, the data should be honest, which also addresses the bad data problem below.

Each session records:
- Spot, date and time
- Board and wetsuit used
- Wave size and number of waves caught
- Session rating

What the surfer gets back:
- Their gear and board history, and what worked in which conditions
- How they surfed over the year

What the forecast gets:
- Accurate observed conditions per spot and time, joined to the stored prediction for that moment

Requires user accounts and profiles (currently a non goal; this moves it into scope for stage 06).

## Trust and bad data
Community ratings (spots rated up or down) are a goal, but surfers may deliberately log bad data on good days to keep crowds away. Options to weigh:
- Verified accounts only, no anonymous submissions
- Reputation weighting: a logger's weight grows as their observations agree with buoy data and other loggers
- Outlier detection: flag observations far from what buoys and the consensus show
- Start with a small trusted group, open up later

## Open questions
- Verify users or not, and how?
- What quality scale is most useful?
