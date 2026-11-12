# Scenario and scouting validation

Checked on 12 November 2026.

- 20 Python tests passed, including the existing analysis suite and the new scouting aggregation checks.
- 10 JavaScript simulation tests passed: strike rotation, target and wicket stopping, bowler scheduling/quota, run-out credit, reproducibility, boundary cases, probability normalization and SR reweighting, invalid inputs, pre-ball pressure and sparse-matchup fallback.
- All 629 eligible player/scope/role scouting totals were reconciled to the existing player-details data for legal balls, bat runs and wickets. Side totals sum to the complete sample. The simulation's Combined league sample contains 181,339 retained deliveries.
- Existing ranking results were unchanged; rebuilt player-details output matched the prior output.
- Browser checks covered scenario execution, saved comparison, SR assumptions, linked required-rate/target inputs, last-wicket preset, export feedback, player-to-simulator navigation, phase filters and bowler handedness maps.
- Desktop (1440 × 1000) and mobile (390 × 844) layouts were inspected in dark and light appearance. The mobile document had no horizontal overflow; wide evidence tables scroll within their panels. The five-button pill navigation remained usable.
- No browser console errors were observed in the final preview.

These checks establish implementation consistency. They do not establish predictive accuracy, probability calibration, authenticity of source annotations, or readiness for operational selection decisions. See [SCENARIO_GUIDE.md](SCENARIO_GUIDE.md) for assumptions and limits.
