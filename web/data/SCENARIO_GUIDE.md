# Scenario lab and scouting evidence

Updated 12 November 2026. This addition supports scouting discussion; it is not a validated selection or live win-prediction service.

## Start here

Open **Simulator** in the glass navigation. Choose a preset, then a batter and bowler. Set whole overs remaining, wickets remaining, and runs needed. Editing required run rate updates the runs needed, rounded to a whole run; the displayed rate is recalculated from that integer target. Run 2,000 possible finishes. Save a result as a comparison baseline, change one input, and run again. Export includes settings, player names, outcome summaries, seed and limitations.

Player Lab also has **Try this player in a scenario**. It carries the selected player and competition into the simulator. Eligible batting and bowling pools are the same as the existing rankings. An all-rounder may be selectable in either role, but cannot face himself.

## Player Lab additions

- A field-side diagram shades **off side** and **leg/on side** by the share of tagged runs. It uses the supplied `on_or_off` annotations. For a bowler, these are runs conceded off the bat, filtered by the batter's right/left handedness. The diagram mirrors for left-handers and labels the viewing direction.
- The field is a two-region summary, not a tracked wagon wheel. The source has no exact shot angles, distances, fielder coordinates or pitch coordinates. Some stroke names disagree with side tags; neither is silently rewritten from the other. The diagram should not be used to infer exact field placement.
- Batters are split by bowling style. Bowlers are split by batter hand. Additional tables show delivery variations, shot labels and the 12 most-faced opponents, selected by ball count rather than performance.
- The phase filter applies to the map and all scouting tables. The bowler handedness control changes only the map. Existing scope filters continue to separate IPL, T20I and Combined.
- Headline favorable/difficult comparisons require **30 balls and 3 distinct matches** in each comparison group. They compare observed SR for batters, and bat runs per six balls for bowlers. These thresholds are display safeguards, not significance tests. Wickets, dots and sample sizes remain visible; no permanent weakness or causal effect is claimed.
- All retained legal balls count in rates; a dot includes a striker-wicket ball with zero bat runs. Wicket counts use striker dismissals for batting and bowler credit for bowling, as in the existing project. Shot tables include unsuccessful attempts, not only scoring strokes.

## Historical model

The same cleaning and exclusions as the ranking pipeline supply **181,339 retained legal deliveries**, without changing any rank or pressure score. Player scouting data loads on demand; the simulation count model loads when Simulator is opened.

Each ball is one of 21 joint categories: 0–6 bat runs, combined with (a) no striker dismissal, (b) bowler-credited striker dismissal, or (c) another striker dismissal. Therefore a run-out can remove a batter without giving the bowler a wicket, and nonzero runs on a dismissal are not lost.

League phase distributions shrink toward the complete competition pool with 200 prior balls. Pressure-context distributions shrink toward phase distributions with 200 prior balls. Player distributions progressively use the player's full sample, phase sample, pressure-context sample and applicable style/hand sample, each with 60 prior balls. A tiny positive floor in the broad pool prevents impossible zero-probability categories due solely to sparse data.

For a specific batter facing a specific bowler, the two smoothed player distributions are averaged to form a prior. Their direct, same-context head-to-head counts are then blended with **120 prior balls**:

`probability(outcome) = (direct count + 120 × blended prior probability) / (direct sample size + 120)`

Direct evidence weight is `N / (N + 120)`. Zero direct balls means zero direct weight; the interface explicitly reports the fallback. Samples at successive levels overlap; the prior strengths are heuristic regularization choices, not independent evidence counts or fitted optimal hyperparameters.

## Simulated innings rules

1. A scenario begins at the start of an over in a standard 20-over innings. The chosen batter is on strike, with a peer-average non-striker.
2. Phases are Powerplay (1–6), Middle (7–15) and Death (16–20). The existing pre-ball pressure proxy uses phase, wickets lost, recent wicket clusters and optional knockout status. Required run rate sets the target, but does not itself alter the batting distribution.
3. Strike swaps on odd runs and after six legal balls. A dismissed selected batter does not return. Replacement batters and the initial partner use peer distributions; the actual remaining XI is not known.
4. The chosen bowler bowls the next over and then alternate overs, limited by the supplied remaining quota and a maximum of four. Other overs use peer distributions. Actual bowling allocations may differ.
5. Stop at the target, zero wickets remaining, or the final legal ball. A target reached on a boundary can be exceeded by that boundary. Ended paths remain flat in the trajectory plot.
6. The optional “two recent wickets” setting places falls in the previous two balls; at least two wickets must already have fallen. The user should leave it off if recent timing is unknown.
7. The fixed seed is **20261112**, with **2,000 trials**. A saved baseline remains in browser memory for the current page session. It is not uploaded or shared.

## Optional strike-rate what-if

With the override off, scoring and dismissal probabilities come from the historical model. With it on, non-wicket scoring probabilities are exponentially reweighted to approach the requested bat runs per ball (`SR / 100`). Wicket probabilities and their associated runs remain unchanged. This is a scoring-only sensitivity exercise; it does **not** estimate how extra aggression changes dismissal risk. Extreme requested rates can be limited by the distribution's support. It is not an instruction that guarantees the batter will score at that rate.

## Reading outputs

- **Target reached:** percentage of simulated, bat-runs-only finishes reaching the entered target. It is **not an official or calibrated match win probability**.
- **Batter additional runs:** median with the 10th–90th percentile range, including dismissals and time off strike.
- **Bowler average figures:** mean credited wickets and bat runs conceded, plus the mean balls actually bowled before the simulated innings stops.
- **Trajectory:** median team bat runs and the middle 80% of simulated paths. This is an outcome range conditional on the model, not a confidence interval for true performance.
- **Comparison:** descriptive change between saved and current scenarios. Changing multiple assumptions makes attribution difficult. Common seeds reduce some Monte Carlo noise but do not prove causal effects.

## Limits before operational use

The pack's extras fields are undocumented/type-coded, so no extras are simulated. Non-striker dismissals, exact chase pressure, actual teammate ability, pitch, weather, dew, fielding plans, injuries, fatigue, recent tactical changes and contract/fitness availability are absent. Source dates and shot annotations are not independently verified. Distributions are historical summaries, not trained causal response models.

No held-out forecasting calibration has been completed. Before any professional reliance: obtain a licensed and verified scoring/shot feed, reconcile IDs and team totals, back-test on later matches not used to fit the model, measure calibration by scenario/sample size, and retain analyst review. The existing project guide PDF predates these additions; this document is the current supplement.

## Internet references checked

- [ICC playing conditions](https://www.icc-cricket.com/about/cricket/rules-and-regulations/playing-conditions): reference for standard T20 innings and bowling restrictions; this model remains simplified.
- [ICC over rules](https://www.icc-cricket.com/news/mens-t20i-match-clause-17-the-over): no consecutive overs by the same bowler.
- [ICC 2026 Men's T20 World Cup playing conditions](https://images.icc-cricket.com/image/upload/prd/igqt8cceiusrtat0ru5u.pdf): four-over maximum in a standard innings.
- [Cricsheet JSON schema](https://cricsheet.org/format/json/): an example of a structured feed that distinguishes batter runs, extras and total runs for future score reconstruction. No external match rows were mixed into the supplied pack. The consulted delivery schema does not provide tracked shot coordinates.

## Rebuild and verify

Run from the project folder:

```powershell
python -m analysis.build --data-dir data/raw
python -m unittest discover -s tests -v
node tests/test_scenario_engine.js
```

Node is required only for the JavaScript development checks; running the dashboard still needs only Python. The build writes `web/data/insights/<scope>/<role>/<player>.json`, the small insights index and `simulation_data.json`. Existing rankings and player-details outputs were reconciled against their prior versions when adding this feature.
