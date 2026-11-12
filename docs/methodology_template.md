# SupeRR Selector: performance when the situation matters

## Research question

Which batters and bowlers repeatedly perform well in pivotal T20 situations, relative to comparable deliveries and their own ordinary-situation baseline? The two final lists are separate rankings, not a balanced playing XI. A player can qualify in both categories. Ratings are historical descriptive evidence from the supplied pack, not forecasts or claims about current squads.

## Data integrity comes first

The six supplied CSVs are joined using match, competition and player IDs. Player mappings provide names and teams; playing XIs provide a cross-check. The teams file is preserved and fingerprinted for provenance, but the analysis uses team labels from matches and player mappings. Source rows are ordered by match, innings and innings_ball_num. Duplicate delivery keys are removed, with counts recorded. Innings with gaps in that sequence or more than six identifiable legal deliveries in an over are quarantined.

Only IPL and T20I competitions are included. Other domestic T20 competitions, super overs and matches with revised targets/overs are excluded. A source innings is considered usable if it passes these sequence checks; these checks cannot prove a truncated source innings is complete. Match metadata dates are authoritative within this pack.

**Critical source issue:** extras1_runs is a type code, not a trustworthy run amount. Observed codes are None=6, wide=2, legbyes=3, byes=4, Overstep=1, other=5, Penalty=7. The meaning of extras_2_runs is not documented. Neither field is added to team totals. No exact chase score, required run rate or official bowling economy is fabricated.

Performance calculations use identifiable legal deliveries: None, blank, byes and legbyes. Overstep, wide, other and Penalty rows are excluded from performance denominators and numerators, although wicket flags on those rows still update the pre-delivery match state. A retired/obstructing wicket can affect team wickets but is not charged as a striker dismissal in the performance metric. Non-striker runouts are not charged to the striker.

## Pressure definition

Pressure is a transparent **shared pivotal-situation proxy** for batting and bowling. It does not mean the same tactical difficulty for each side. It is calculated before each delivery, from innings phase, wickets already lost, previous wickets and knockout stage. The delivery's runs and wicket never enter its own pressure score.

| Signal | Points |
|---|---:|
| Base in overs 1–6 | 10 |
| Base in overs 7–15 | 20 |
| Base in overs 16–18 | 60 |
| Base in overs 19–20 | 75 |
| At least 3 wickets already down, in overs 1–10 | +30 |
| Otherwise, at least 4 wickets already down, in overs 11–15 | +20 |
| At least 2 wickets within the previous 12 legal balls | +20 |
| Final, Semi Final, Qualifier or Eliminator | +10 |

Cap at 100. High pressure is **55 or higher**; ordinary is below 55. Wicket recency uses completed legal-ball positions: a wicket falls out of the window after 12 subsequent legal balls. Thresholds 50 and 65 are sensitivity alternatives. Scores and thresholds are analyst assumptions, not empirically calibrated probabilities. Overs are the source's one-based overid values.

Late overs create concentrated scoring opportunities; clusters of wickets identify potentially decisive passages. These are available without inventing extras. A future version with verified team totals should distinguish close finishes from decided games and model batting and bowling difficulty separately. The current model can mark a one-sided finish as high pressure and a collapse as pivotal even when it makes the bowler's task easier.

## Performance measures and context

For batters, measure legal-ball strike rate (100 × runs off bat / legal balls), striker dismissals per 100 legal balls, boundary-ball percentage and zero-bat-run percentage. These are deliberately labelled legal-ball measures; legal-ball strike rate is not official strike rate because no-ball batting runs/balls are omitted.

For bowlers, measure bat runs conceded per six legal deliveries and credited wickets per 100 legal deliveries. Bowled, Caught, LBW, Stump and Hit Wicket are credited. Runouts, retired out and obstructing the field are not. Bat runs per six is **not economy**, because wides, no-ball penalties and all other extras are omitted. A zero-bat-run delivery need not be a scoreless team delivery when byes occur.

Build peer groups separately for batting and bowling. The finest grouping is format (IPL/T20I), calendar year, innings number, phase and batting-order group (1–3, 4–7, 8–11) or bowling type (pace/spin). Require 200 deliveries; otherwise drop year, then drop role/type. The broadest group is used even if it remains below 200. IPL and T20I remain separate in all group levels. The broadest groups are not independent of the players they evaluate, so these are descriptive residuals rather than out-of-sample estimates.

Let expected runs and wicket probability be the peer-group means. Standardize run deviations by peer run standard deviation (floor 0.5) and wicket deviations by sqrt(p × (1-p)) (floor 0.1).

- Batting delivery impact = 0.65 × standardized runs above expectation + 0.35 × standardized dismissals avoided.
- Bowling delivery impact = 0.65 × standardized runs prevented + 0.35 × standardized wickets above expectation.

Positive impact is better than context expectation. Zero is context average. Compare pressure and ordinary averages after this adjustment, since raw rates from different phases are not directly comparable. Phase-based pressure and phase-based peer adjustment intentionally answer different questions: pressure selects situations; peer adjustment asks whether the player outperformed comparable deliveries.

## Eligibility and rating

Each candidate must have at least **60 pressure balls**, **60 ordinary balls**, and **8 pressure matches containing at least 6 pressure balls each**. These gates are pragmatic minimums, not a guarantee of statistical certainty. All pressure balls contribute to performance; matches below six pressure balls do not count toward consistency or the eight-match gate. Excluded-player reasons are available in the dashboard. Scope-specific lists recompute eligibility and percentiles inside that scope. The Combined list is the fixed submission output.

1. **Pressure performance (50%)**: mean context-adjusted pressure impact × n_pressure / (n_pressure + 60). This shrinks small samples toward the context average of zero.
2. **Baseline uplift (30%)**: difference between pressure and ordinary mean impact × n_effective / (n_effective + 60), where n_effective = n_pressure × n_ordinary / (n_pressure + n_ordinary).
3. **Repeatability (20%)**: (positive-impact pressure matches + 2) / (qualifying pressure matches + 4). This is a smoothed above-context match fraction, not a confidence probability.

Convert each component to a mid-rank percentile among eligible players in the same category/scope. Weighted sum gives a 0–100 relative rating. A score of 80 is not an 80% chance of success. Ties break on more pressure balls, then player ID. Batting and bowling scores are not directly comparable. The 65/35 delivery weights, 50/30/20 final weights, 60-ball shrinkage and eligibility gates are documented modelling choices, not fitted optimums.

## Reliability checks

Recompute rankings for pressure thresholds 50 and 65, scoring weights 60/20/20 and 40/40/20, and removal of each player's single highest-total-impact pressure match. In the removal scenario, remove that player's pressure contributions from that match only, keep ordinary baselines and context expectations fixed, and reapply eligibility. Display the minimum and maximum observed rank across these five alternatives plus the default, and show ineligible scenarios explicitly. Because eligibility pools change, rank changes combine performance and population effects.

This is sensitivity analysis, **not a confidence interval**. Season and match evidence is displayed separately. No train/test evaluation, predictive claim, opponent-strength correction or external data validation is implied. Unit checks cover pressure timing, dismissal attribution, extras treatment, context signs, eligibility and percentile ties.

## Submission and interpretation

Use the two Combined top-10 lists for the Unstop dropdowns, ensuring ordering matches this report. Exploratory IPL/T20I lists should not silently replace that submission. Inspect each player's evidence and sensitivity before submitting. The report and dashboard are reproducible from the same calculation, so values remain aligned.
