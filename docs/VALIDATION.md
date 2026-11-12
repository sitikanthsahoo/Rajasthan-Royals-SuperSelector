# Validation record

Validated on 11 November 2026 against the supplied data pack.

## Automated checks

Command: `python -m unittest discover -s tests -v`

15 checks pass:

- Death-over boundaries and pressure cap.
- Collapse scoring and exclusion of current-delivery outcome inputs.
- Runout, caught and non-playing dismissal attribution.
- Legal-delivery classification and bat-run rate denominators.
- Context-adjusted impact averaging to zero within a controlled peer group.
- Direction of batting and bowling impact.
- Mid-rank percentile ties.
- Sample-size shrinkage.
- Match eligibility gates and the six-pressure-ball consistency minimum.
- Every generated list has unique, eligible players in score order.
- Component weights reconcile to the displayed rating.
- Retained and excluded source rows reconcile to the original row count.
- All 803 match-detail files exist; wicket state precedes the current ball in every delivery.
- Pressure-ball counts reconcile between timeline files and the dashboard summary.
- Both report lists match the dashboard's 20 Combined selections.

Some test methods cover multiple related assertions. Both JavaScript files also pass Node's syntax check.

## Browser checks

- Dashboard loads from the local Python server.
- Batting and bowling toggles change the ranking and spotlight.
- Combined/IPL filtering changes the candidate pool and profile.
- Player evidence shows usual/pressure rates, peer expectations and sensitivity scenarios.
- Search finds a named player, and clearing the query restores the list.
- CSV export produces a downloaded top-10 bowling file.
- Match explorer changes innings and the selected over; delivery evidence updates.
- Methodology, audit, exclusions search and reproducibility instructions render.
- Printable report contains both top-10 lists and the limitations.
- Phone layout (390-pixel requested width) has no document-level horizontal overflow.
- Desktop layout (1440-pixel requested width) visually inspected.
- No browser console errors observed during these checks.

## Limits

- Browser interaction checks are a manual development pass, not an exhaustive automated regression suite.
- The report's printable HTML is verified; the user's eventual browser-generated PDF must be visually checked before upload.
- The source's extras ambiguity cannot be resolved by software tests. Rates, pressure definition and limitations deliberately reflect this constraint.
- Source date/identity authenticity, official scorecard reconciliation, causality, predictive accuracy and competition acceptance are not established by these checks.
- The repository is prepared for GitHub but no remote repository was created or pushed.
