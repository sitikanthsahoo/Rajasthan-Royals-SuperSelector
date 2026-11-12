# Player intelligence upgrade

The player lab now includes sourced portraits and profile links, country/representation, an IPL roster snapshot when verified, activity evidence, historical team mappings, sample averages and strike rates, overlapping pressure-situation cards and eight recent matches with a situation selector.

## Source separation

- Historical analytics use only the supplied dataset through 2026-11-01.
- `web/data/profiles.json` contains 148 external profile snapshots checked 2026-11-11: 139 official IPL, eight ICC and one Cricbuzz. All 20 Combined top-10 selections have portrait references.
- Remaining eligible players display initials and explicitly unverified external fields. No nationality or citizenship is inferred from names, birthplace or a franchise affiliation.
- IPL profiles indicate the franchise displayed at retrieval, not a guarantee of a contract, auction registration, fitness or availability for a future match. ICC appearance years are activity evidence, not confirmation of a current national-team place.
- Portraits are remote references credited to publishers. Failed images fall back to initials. Internet is needed for portraits and source pages; the numeric dashboard works locally.

## Pakistan review flags

An amber row and text badge indicate Pakistan international representation in the supplied player-team mapping. These players remain in all relevant lists, with unchanged scores. The flag requests an individual check of IPL registration, current passport/nationality rules and board clearance, accounting for exceptions. It is not a permanent-ban determination. Context: https://www.cricbuzz.com/cricket-news/140773/mohammad-amir-rules-out-entering-ipl-auction

## Statistics and recency

All new numeric summaries reuse the retained legal-ball events and existing context-adjusted impacts. Batting average is retained bat runs / retained striker dismissals; bowling average is bat runs conceded / credited wickets. These sample averages are not official career averages. A zero wicket/dismissal denominator is null and displayed as a dash. Bowling strike rate is legal balls / wickets; batting strike rate is 100 x bat runs / legal balls.

Recent matches are the latest eight retained appearances for the selected role and competition, sorted by date then ID. Matches with no qualifying pressure situation remain visible with no-sample values. They are not the eight best performances. The existing match-evidence table lower down remains explicitly ordered by highest total pressure impact.

Situation buckets include only deliveries with pressure >= 55: death overs, early/middle wicket-loss conditions, two recent wickets in 12 legal balls, and knockout stages. Buckets overlap and must not be added. The under-30-ball small-sample cue is informational, not a ranking gate.

## Reproduce

```powershell
py -m analysis.build --data-dir data/raw
py -m analysis.enrich_profiles
py -m analysis.international_profiles
py -m unittest discover -s tests
py app.py
```

Run both enrichment commands in that order to retain international shortlist coverage. Their public HTML caches go into `tmp/profile-sources/`; exclude that directory from Git. No API keys are needed. Source sites may change their structure: review refresh errors and source dates before relying on refreshed profiles.

The project guide is at `output/pdf/SupeRR_Selector_Project_Guide.pdf`, with a downloadable copy at `web/data/PROJECT_GUIDE.pdf`. Regeneration uses `docs/build_project_guide.py` with ReportLab installed; ReportLab is not required to run the app.

## Validation

17 analysis tests passed. New tests cover date ordering, zero-pressure appearances, null averages, scope isolation and overlapping situations. Every ranking object matches the pre-upgrade data. Browser verification covered player selection persistence, official portrait loading, availability flags, situation selection, mobile overflow and both themes.
