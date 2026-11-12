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


## Dataset coverage

The supplied pack contains 200,999 delivery rows and 883 match records. The analysis retains 181,339 legal deliveries in 803 matches, from 2022-01-22 to 2026-11-01. 48,118 retained deliveries meet the default pressure threshold.

## Final combined rankings

### Top 10 batters

| Rank | Player | Rating | Pressure balls | Pressure matches | Scenario rank range |
|---|---|---|---|---|---|
| 1 | Akeal Hosein | 96.11 | 152 | 11 | 1–2 |
| 2 | Najibullah Zadran | 95.93 | 107 | 8 | 1–2 |
| 3 | Jacob Bethell | 94.96 | 90 | 8 | 3–11 |
| 4 | Rashid Khan | 93.27 | 409 | 25 | 1–21 |
| 5 | Ramandeep Singh | 90.62 | 122 | 10 | 2–5 |
| 6 | Suryakumar Yadav | 86.64 | 445 | 33 | 2–17 |
| 7 | Rinku Singh | 84.42 | 670 | 51 | 4–13 |
| 8 | Rishabh Pant | 83.89 | 264 | 16 | 7–14 |
| 9 | Ashutosh Sharma | 83.63 | 230 | 16 | 4–14 |
| 10 | Nurul Hasan | 83.45 | 134 | 12 | 6–34 |

#### 1. Akeal Hosein

Legal-ball strike rate 155.3 under pressure; context expectation 122.7. Striker dismissals 7.24 per 100 legal balls; context expectation 9.28. Context-adjusted pressure impact is above this player's ordinary-situation baseline (+0.147 vs -0.177). Above-context impact in 8 of 11 pressure matches with at least six balls.

Limitation: Pressure is a phase/wicket proxy; exact chase difficulty and official economy cannot be recovered from the supplied extras fields. Ineligible in 2 of five alternative scenarios.

#### 2. Najibullah Zadran

Legal-ball strike rate 199.1 under pressure; context expectation 163.7. Striker dismissals 4.67 per 100 legal balls; context expectation 6.83. Context-adjusted pressure impact is above this player's ordinary-situation baseline (+0.149 vs -0.106). Above-context impact in 7 of 8 pressure matches with at least six balls.

Limitation: Pressure is a phase/wicket proxy; exact chase difficulty and official economy cannot be recovered from the supplied extras fields. Ineligible in 2 of five alternative scenarios.

#### 3. Jacob Bethell

Legal-ball strike rate 196.7 under pressure; context expectation 152.4. Striker dismissals 5.56 per 100 legal balls; context expectation 8.11. Context-adjusted pressure impact is above this player's ordinary-situation baseline (+0.183 vs -0.013). Above-context impact in 6 of 8 pressure matches with at least six balls.

Limitation: Pressure is a phase/wicket proxy; exact chase difficulty and official economy cannot be recovered from the supplied extras fields. Ineligible in 2 of five alternative scenarios.

#### 4. Rashid Khan

Legal-ball strike rate 162.1 under pressure; context expectation 129.3. Striker dismissals 8.56 per 100 legal balls; context expectation 8.84. Context-adjusted pressure impact is above this player's ordinary-situation baseline (+0.132 vs +0.035). Above-context impact in 18 of 25 pressure matches with at least six balls.

Limitation: Pressure is a phase/wicket proxy; exact chase difficulty and official economy cannot be recovered from the supplied extras fields.

#### 5. Ramandeep Singh

Legal-ball strike rate 169.7 under pressure; context expectation 139.4. Striker dismissals 6.56 per 100 legal balls; context expectation 8.15. Context-adjusted pressure impact is above this player's ordinary-situation baseline (+0.126 vs -0.095). Above-context impact in 7 of 10 pressure matches with at least six balls.

Limitation: Pressure is a phase/wicket proxy; exact chase difficulty and official economy cannot be recovered from the supplied extras fields. Ineligible in 1 of five alternative scenarios.

#### 6. Suryakumar Yadav

Legal-ball strike rate 204.0 under pressure; context expectation 166.2. Striker dismissals 6.29 per 100 legal balls; context expectation 6.65. Context-adjusted pressure impact is above this player's ordinary-situation baseline (+0.141 vs +0.120). Above-context impact in 22 of 33 pressure matches with at least six balls.

Limitation: Pressure is a phase/wicket proxy; exact chase difficulty and official economy cannot be recovered from the supplied extras fields.

#### 7. Rinku Singh

Legal-ball strike rate 178.8 under pressure; context expectation 164.5. Striker dismissals 4.63 per 100 legal balls; context expectation 7.14. Context-adjusted pressure impact is above this player's ordinary-situation baseline (+0.082 vs -0.016). Above-context impact in 30 of 51 pressure matches with at least six balls.

Limitation: Pressure is a phase/wicket proxy; exact chase difficulty and official economy cannot be recovered from the supplied extras fields.

#### 8. Rishabh Pant

Legal-ball strike rate 188.3 under pressure; context expectation 175.0. Striker dismissals 6.06 per 100 legal balls; context expectation 6.98. Context-adjusted pressure impact is above this player's ordinary-situation baseline (+0.056 vs -0.017). Above-context impact in 13 of 16 pressure matches with at least six balls.

Limitation: Pressure is a phase/wicket proxy; exact chase difficulty and official economy cannot be recovered from the supplied extras fields. Ineligible in 1 of five alternative scenarios.

#### 9. Ashutosh Sharma

Legal-ball strike rate 183.5 under pressure; context expectation 160.6. Striker dismissals 6.09 per 100 legal balls; context expectation 7.96. Context-adjusted pressure impact is above this player's ordinary-situation baseline (+0.104 vs +0.044). Above-context impact in 11 of 16 pressure matches with at least six balls.

Limitation: Pressure is a phase/wicket proxy; exact chase difficulty and official economy cannot be recovered from the supplied extras fields.

#### 10. Nurul Hasan

Legal-ball strike rate 151.5 under pressure; context expectation 152.5. Striker dismissals 2.24 per 100 legal balls; context expectation 7.71. Context-adjusted pressure impact is above this player's ordinary-situation baseline (+0.067 vs -0.196). Above-context impact in 8 of 12 pressure matches with at least six balls.

Limitation: Pressure is a phase/wicket proxy; exact chase difficulty and official economy cannot be recovered from the supplied extras fields. Ineligible in 1 of five alternative scenarios.
### Top 10 bowlers

| Rank | Player | Rating | Pressure balls | Pressure matches | Scenario rank range |
|---|---|---|---|---|---|
| 1 | Sunil Narine | 98.75 | 346 | 41 | 1–2 |
| 2 | Mohammad Nawaz | 98.37 | 143 | 13 | 2–3 |
| 3 | Sufiyan Muqeem | 97.77 | 115 | 11 | 1–7 |
| 4 | Shadab Khan | 96.14 | 144 | 16 | 4–8 |
| 5 | Craig Young | 94.57 | 103 | 11 | 5–9 |
| 6 | Sakib Hussain | 94.40 | 91 | 11 | 6–21 |
| 7 | Kuldeep Yadav | 94.35 | 423 | 52 | 3–21 |
| 8 | Jasprit Bumrah | 93.91 | 603 | 63 | 5–11 |
| 9 | Abrar Ahmed | 93.42 | 203 | 19 | 4–16 |
| 10 | Joshua Little | 92.99 | 211 | 28 | 8–47 |

#### 1. Sunil Narine

Concedes 5.84 bat runs per six legal balls under pressure; context expectation 8.86. Takes 7.23 credited wickets per 100 legal balls; context expectation 6.28. Context-adjusted pressure impact is above this player's ordinary-situation baseline (+0.191 vs +0.064). Above-context impact in 32 of 41 pressure matches with at least six balls.

Limitation: Pressure is a phase/wicket proxy; exact chase difficulty and official economy cannot be recovered from the supplied extras fields.

#### 2. Mohammad Nawaz

Concedes 5.16 bat runs per six legal balls under pressure; context expectation 7.78. Takes 8.39 credited wickets per 100 legal balls; context expectation 6.12. Context-adjusted pressure impact is above this player's ordinary-situation baseline (+0.209 vs +0.019). Above-context impact in 10 of 13 pressure matches with at least six balls.

Limitation: Pressure is a phase/wicket proxy; exact chase difficulty and official economy cannot be recovered from the supplied extras fields. Ineligible in 1 of five alternative scenarios.

#### 3. Sufiyan Muqeem

Concedes 5.01 bat runs per six legal balls under pressure; context expectation 7.40. Takes 10.43 credited wickets per 100 legal balls; context expectation 8.40. Context-adjusted pressure impact is above this player's ordinary-situation baseline (+0.210 vs +0.019). Above-context impact in 9 of 11 pressure matches with at least six balls.

Limitation: Pressure is a phase/wicket proxy; exact chase difficulty and official economy cannot be recovered from the supplied extras fields. Ineligible in 1 of five alternative scenarios.

#### 4. Shadab Khan

Concedes 5.38 bat runs per six legal balls under pressure; context expectation 7.78. Takes 6.94 credited wickets per 100 legal balls; context expectation 6.58. Context-adjusted pressure impact is above this player's ordinary-situation baseline (+0.175 vs -0.076). Above-context impact in 11 of 16 pressure matches with at least six balls.

Limitation: Pressure is a phase/wicket proxy; exact chase difficulty and official economy cannot be recovered from the supplied extras fields. Ineligible in 1 of five alternative scenarios.

#### 5. Craig Young

Concedes 6.99 bat runs per six legal balls under pressure; context expectation 9.25. Takes 8.74 credited wickets per 100 legal balls; context expectation 7.45. Context-adjusted pressure impact is above this player's ordinary-situation baseline (+0.154 vs -0.010). Above-context impact in 8 of 11 pressure matches with at least six balls.

Limitation: Pressure is a phase/wicket proxy; exact chase difficulty and official economy cannot be recovered from the supplied extras fields. Ineligible in 1 of five alternative scenarios.

#### 6. Sakib Hussain

Concedes 7.78 bat runs per six legal balls under pressure; context expectation 10.07. Takes 8.79 credited wickets per 100 legal balls; context expectation 6.52. Context-adjusted pressure impact is above this player's ordinary-situation baseline (+0.161 vs -0.010). Above-context impact in 9 of 11 pressure matches with at least six balls.

Limitation: Pressure is a phase/wicket proxy; exact chase difficulty and official economy cannot be recovered from the supplied extras fields. Ineligible in 1 of five alternative scenarios.

#### 7. Kuldeep Yadav

Concedes 7.28 bat runs per six legal balls under pressure; context expectation 8.79. Takes 9.22 credited wickets per 100 legal balls; context expectation 6.50. Context-adjusted pressure impact is above this player's ordinary-situation baseline (+0.137 vs +0.012). Above-context impact in 33 of 52 pressure matches with at least six balls.

Limitation: Pressure is a phase/wicket proxy; exact chase difficulty and official economy cannot be recovered from the supplied extras fields.

#### 8. Jasprit Bumrah

Concedes 7.02 bat runs per six legal balls under pressure; context expectation 9.96. Takes 7.13 credited wickets per 100 legal balls; context expectation 7.24. Context-adjusted pressure impact is above this player's ordinary-situation baseline (+0.167 vs +0.096). Above-context impact in 48 of 63 pressure matches with at least six balls.

Limitation: Pressure is a phase/wicket proxy; exact chase difficulty and official economy cannot be recovered from the supplied extras fields.

#### 9. Abrar Ahmed

Concedes 5.50 bat runs per six legal balls under pressure; context expectation 7.99. Takes 7.39 credited wickets per 100 legal balls; context expectation 7.48. Context-adjusted pressure impact is above this player's ordinary-situation baseline (+0.162 vs +0.051). Above-context impact in 13 of 19 pressure matches with at least six balls.

Limitation: Pressure is a phase/wicket proxy; exact chase difficulty and official economy cannot be recovered from the supplied extras fields. Ineligible in 1 of five alternative scenarios.

#### 10. Joshua Little

Concedes 7.85 bat runs per six legal balls under pressure; context expectation 9.52. Takes 8.53 credited wickets per 100 legal balls; context expectation 7.14. Context-adjusted pressure impact is above this player's ordinary-situation baseline (+0.118 vs +0.001). Above-context impact in 20 of 28 pressure matches with at least six balls.

Limitation: Pressure is a phase/wicket proxy; exact chase difficulty and official economy cannot be recovered from the supplied extras fields.

## Audit counts

- non legal or ambiguous rows excluded: 8,095
- non striker dismissals not charged to striker: 255
- revised match rows excluded: 4,433
- super over rows excluded: 38
- other competition rows excluded: 6,973
- wickets missing dismissed player: 1
- quarantined rows: 121

## Limitations

- extras1_runs maps to extras-type codes, including 6 on ordinary deliveries. It is not summed as runs. extras_2_runs is undocumented and not interpreted as an amount.
- Exact team totals, chase targets, required run rate, official strike rate and official bowling economy are not claimed.
- Pressure is a shared phase/wicket situation proxy, not a psychological measure or calibrated win probability. One-sided death overs can still be marked high pressure; a batting collapse may favour the bowler.
- Legal-ball batting strike rate excludes no-balls. Bat runs per six legal balls excludes all extras. Striker-dismissal rate excludes non-striker runouts and non-playing dismissals.
- Peer groups adjust for format, phase, innings and where supported year and batting position/bowling type. Opponent strength, exact venue effects, dew and pitch quality are not adjusted.
- Context expectations use the full supplied sample. These are descriptive historical rankings, not out-of-sample predictions.
- Reduced/revised matches, super overs, other T20 competitions, ambiguous/non-legal deliveries and malformed innings are excluded as documented in the audit.
- Scenario rank ranges measure sensitivity, not statistical confidence intervals. Eligibility and peer populations may change between scenarios.
- Dates and identities are accepted from the supplied pack without external verification; no current-form or squad-availability claim is made.

## Reproduce

Run `python -m analysis.build --data-dir data/raw` from the project root. Run `python -m unittest discover -s tests -v` for the calculation checks. Source SHA-256 hashes are recorded in `reports/data_audit.json`. No random seed is needed: the pipeline is deterministic apart from its build timestamp.
