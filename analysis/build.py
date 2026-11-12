"""Build the dashboard data from the supplied CSVs. Python 3.10+, standard library only."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
LEGAL = {"None", "", "byes", "legbyes"}
BOWLER_WICKETS = {"Caught", "Bowled", "LBW", "Stump", "Hit Wicket"}
MIN_BALLS = 60
MIN_MATCHES = 8
THRESHOLD = 55
PRIOR_BALLS = 60


def number(value, default=0):
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default


def truth(value):
    return str(value).lower() in {"true", "1"}


def dismissal_flags(wicket, dismissed, striker, kind):
    """Separate striker dismissals from bowler-credit events (especially runouts)."""
    non_playing = {"Retire Out", "Obstracting the field", "Obstructing the field"}
    return (int(wicket and dismissed == striker and kind not in non_playing),
            int(wicket and kind in BOWLER_WICKETS))


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def phase(over):
    return "Powerplay" if over <= 6 else "Middle" if over <= 15 else "Death"


def pressure(over, wickets, recent_wickets, knockout=False):
    """Only pre-delivery inputs; this is a pivotal-situation proxy, not win probability."""
    score = 10 if over <= 6 else 20 if over <= 15 else 60 if over <= 18 else 75
    reasons = []
    if over >= 16:
        reasons.append("Death overs")
    if over <= 10 and wickets >= 3:
        score += 30
        reasons.append("Early wicket losses")
    elif over <= 15 and wickets >= 4:
        score += 20
        reasons.append("Middle-innings wicket losses")
    if recent_wickets >= 2:
        score += 20
        reasons.append("Two wickets in previous 12 legal balls")
    if knockout:
        score += 10
        reasons.append("Knockout stage")
    return min(score, 100), reasons or ["Ordinary phase"]


def json_write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False), encoding="utf-8")


def accumulator():
    return {"balls": 0, "runs": 0, "wickets": 0, "dots": 0, "boundaries": 0,
            "utility": 0.0, "expected_runs": 0.0, "expected_wickets": 0.0}


def add(a, event, role):
    a["balls"] += 1
    a["runs"] += event["runs"]
    a["wickets"] += event["bw" if role == "bowlers" else "out"]
    a["dots"] += event["runs"] == 0
    a["boundaries"] += event["boundary"]
    a["utility"] += event["bu" if role == "bowlers" else "au"]
    a["expected_runs"] += event["be" if role == "bowlers" else "ae"][0]
    a["expected_wickets"] += event["be" if role == "bowlers" else "ae"][1]


def summary(a):
    n = a["balls"]
    return {"balls": n, "runs": a["runs"], "wickets": a["wickets"],
            "sr": round(100 * a["runs"] / n, 2) if n else None,
            "run_rate": round(6 * a["runs"] / n, 2) if n else None,
            "wicket_rate": round(100 * a["wickets"] / n, 2) if n else None,
            "dot_pct": round(100 * a["dots"] / n, 2) if n else None,
            "boundary_pct": round(100 * a["boundaries"] / n, 2) if n else None,
            "expected_sr": round(100 * a["expected_runs"] / n, 2) if n else None,
            "expected_run_rate": round(6 * a["expected_runs"] / n, 2) if n else None,
            "expected_wicket_rate": round(100 * a["expected_wickets"] / n, 2) if n else None,
            "impact": round(a["utility"] / n, 5) if n else None}


def context_key(e, role, level=0):
    base = (e["format"], e["phase"], e["innings"])
    role_group = e["bat_role"] if role == "batters" else e["style"]
    return base + ((e["year"], role_group) if level == 0 else (role_group,) if level == 1 else ())


def attach_context(events):
    """Use progressively broader descriptive peer groups with at least 200 legal balls."""
    for role in ("batters", "bowlers"):
        groups = [defaultdict(lambda: [0, 0, 0, 0]) for _ in range(3)]
        wicket_key = "out" if role == "batters" else "bw"
        for e in events:
            for level in range(3):
                a = groups[level][context_key(e, role, level)]
                a[0] += 1
                a[1] += e["runs"]
                a[2] += e["runs"] ** 2
                a[3] += e[wicket_key]
        for e in events:
            a = None
            for level in range(3):
                a = groups[level][context_key(e, role, level)]
                if a[0] >= 200:
                    break
            n, runs, squared, wickets = a
            er, ew = runs / n, wickets / n
            rsd = max(math.sqrt(max(0, squared / n - er ** 2)), 0.5)
            wsd = max(math.sqrt(ew * (1 - ew)), 0.1)
            if role == "batters":
                u = .65 * (e["runs"] - er) / rsd + .35 * (ew - e["out"]) / wsd
                e["ae"], e["au"] = (er, ew), u
            else:
                u = .65 * (er - e["runs"]) / rsd + .35 * (e["bw"] - ew) / wsd
                e["be"], e["bu"] = (er, ew), u


def components(p, normal, matches):
    n, ordinary = p["balls"], normal["balls"]
    pm = p["utility"] / n if n else 0
    nm = normal["utility"] / ordinary if ordinary else 0
    effective = n * ordinary / (n + ordinary) if n + ordinary else 0
    reliable_matches = [a for a in matches.values() if a["balls"] >= 6]
    successes = sum(a["utility"] > 0 for a in reliable_matches)
    return {
        "quality": pm * n / (n + PRIOR_BALLS),
        "uplift": (pm - nm) * effective / (effective + PRIOR_BALLS),
        "consistency": (successes + 2) / (len(reliable_matches) + 4),
        "successful_matches": successes,
        "pressure_matches": len(reliable_matches),
    }


def percentile(values, value):
    # Mid-rank percentiles; ties receive identical values, never fake separation.
    below = sum(v < value for v in values)
    equal = sum(v == value for v in values)
    return 100 * (below + .5 * equal) / len(values) if values else 50


def score_rows(rows, weights=(.5, .3, .2)):
    populations = {k: [r[k] for r in rows] for k in ("quality", "uplift", "consistency")}
    for r in rows:
        r["components"] = {k: round(percentile(populations[k], r[k]), 4) for k in populations}
        r["score"] = round(sum(w * r["components"][k] for w, k in zip(weights, populations)), 4)
    rows.sort(key=lambda r: (-r["score"], -r["pressure"]["balls"], r["id"]))
    for rank, r in enumerate(rows, 1):
        r["rank"] = rank
    return rows


def rank(events, players, role, scope="Combined", threshold=THRESHOLD, detail=False, drop_best=False):
    records = {}
    for e in events:
        if scope != "Combined" and e["format"] != scope:
            continue
        pid = e["striker"] if role == "batters" else e["bowler"]
        if pid not in records:
            records[pid] = {"p": accumulator(), "n": accumulator(), "matches": defaultdict(accumulator),
                            "seasons": defaultdict(accumulator), "phases": defaultdict(accumulator)}
        rec = records[pid]
        high = e["pressure"] >= threshold
        add(rec["p"] if high else rec["n"], e, role)
        if high:
            add(rec["matches"][e["match"]], e, role)
            if detail:
                add(rec["seasons"][e["year"]], e, role)
                add(rec["phases"][e["phase"]], e, role)
    rows, excluded = [], []
    for pid, rec in records.items():
        p, normal, matches = rec["p"], rec["n"], rec["matches"]
        if drop_best and matches:
            best = max(matches, key=lambda mid: matches[mid]["utility"])
            removed = matches.pop(best)
            p = {k: p[k] - removed[k] for k in p}
        c = components(p, normal, matches)
        reasons = []
        if p["balls"] < MIN_BALLS:
            reasons.append(f"Fewer than {MIN_BALLS} pressure balls")
        if normal["balls"] < MIN_BALLS:
            reasons.append(f"Fewer than {MIN_BALLS} ordinary balls")
        if c["pressure_matches"] < MIN_MATCHES:
            reasons.append(f"Fewer than {MIN_MATCHES} pressure matches with 6+ balls")
        if reasons:
            excluded.append({"id": pid, "name": players[pid]["name"], "reason": "; ".join(reasons),
                             "pressure_balls": p["balls"], "ordinary_balls": normal["balls"],
                             "pressure_matches": c["pressure_matches"]})
            continue
        row = {"id": pid, **players[pid], **c, "pressure": summary(p), "normal": summary(normal)}
        if detail:
            row["seasons"] = [{"year": year, **summary(a)} for year, a in sorted(rec["seasons"].items())]
            row["phases"] = [{"phase": ph, **summary(a)} for ph, a in rec["phases"].items()]
            row["matches"] = [{"match_id": mid, **summary(a)} for mid, a in matches.items()]
            row["matches"].sort(key=lambda a: a["match_id"])
        rows.append(row)
    return score_rows(rows), sorted(excluded, key=lambda r: (-r["pressure_balls"], r["name"]))


def reasons_for(row, role):
    p, n = row["pressure"], row["normal"]
    if role == "batters":
        performance = f"Legal-ball strike rate {p['sr']:.1f} under pressure; context expectation {p['expected_sr']:.1f}."
        wickets = f"Striker dismissals {p['wicket_rate']:.2f} per 100 legal balls; context expectation {p['expected_wicket_rate']:.2f}."
    else:
        performance = f"Concedes {p['run_rate']:.2f} bat runs per six legal balls under pressure; context expectation {p['expected_run_rate']:.2f}."
        wickets = f"Takes {p['wicket_rate']:.2f} credited wickets per 100 legal balls; context expectation {p['expected_wicket_rate']:.2f}."
    change = "above" if row["uplift"] > 0 else "below" if row["uplift"] < 0 else "at"
    consistency = f"Above-context impact in {row['successful_matches']} of {row['pressure_matches']} pressure matches with at least six balls."
    baseline = f"Context-adjusted pressure impact is {change} this player's ordinary-situation baseline ({p['impact']:+.3f} vs {n['impact']:+.3f})."
    limitation = "Pressure is a phase/wicket proxy; exact chase difficulty and official economy cannot be recovered from the supplied extras fields."
    if row.get("sensitivity_missing", 0):
        limitation += f" Ineligible in {row['sensitivity_missing']} of five alternative scenarios."
    return [performance, wickets, baseline, consistency], limitation


def build(raw_dir, output_dir):
    required = ["ball_by_ball.csv", "matches.csv", "competitions.csv", "competition_team_player_mapping.csv", "playing_eleven.csv", "teams.csv"]
    for name in required:
        if not (raw_dir / name).is_file():
            raise FileNotFoundError(f"Missing {raw_dir / name}. Copy all six supplied CSV files into data/raw/.")
    print("Reading source files...", flush=True)
    matches = {number(r["match_id"]): r for r in read_csv(raw_dir / "matches.csv")}
    comps = {number(r["comp_id"]): r for r in read_csv(raw_dir / "competitions.csv")}
    mappings = read_csv(raw_dir / "competition_team_player_mapping.csv")
    xi = read_csv(raw_dir / "playing_eleven.csv")
    xi_members = {(number(r["match_id"]), number(r["player_id"])) for r in xi if truth(r["is_played"])}
    players = {}
    for r in mappings:
        pid = number(r["player_id"])
        if pid not in players:
            players[pid] = {"name": r["player_name"], "teams": [], "batting_style": "", "bowling_style": ""}
        if r["team_name"] not in players[pid]["teams"]:
            players[pid]["teams"].append(r["team_name"])
    raw = read_csv(raw_dir / "ball_by_ball.csv")
    source_rows = len(raw)
    raw.sort(key=lambda r: (number(r["match_id"]), number(r["innings"]), number(r["innings_ball_num"])))
    audit = Counter()
    extras = defaultdict(Counter)
    for r in raw:
        extras[r["extras_type"]][r["extras1_runs"]] += 1
    meta = {}
    for mid, m in matches.items():
        comp = comps.get(number(m["comp_id"]), {})
        fmt = "IPL" if comp.get("comp_name", "").startswith("IPL ") else "T20I" if comp.get("match_format") == "T20I" else "Other"
        meta[mid] = {"id": mid, "home": m["home_team"], "away": m["away_team"], "date": m["match_date"],
                     "format": fmt, "competition": comp.get("comp_name", "Unknown"), "stage": m["stage"],
                     "result": m["result"], "country": m["venue_country"],
                     "revised": any(m.get(k, "") not in ("", "0", "0.0") for k in ("first_inn_revised_overs", "second_inn_revised_overs", "revised_target"))}
    # Quarantine malformed innings rather than allowing bad sequence data into the ratings.
    groups = defaultdict(list)
    seen = set()
    for r in raw:
        key = (number(r["match_id"]), number(r["innings"]), number(r["innings_ball_num"]))
        if key in seen:
            audit["duplicate_delivery_keys"] += 1
            continue
        seen.add(key)
        groups[key[:2]].append(r)
    events, timelines = [], {}
    context_counts = Counter()
    quarantine = []
    for (mid, innings), rows in groups.items():
        if mid not in meta:
            audit["missing_match_metadata_rows"] += len(rows)
            continue
        m = meta[mid]
        if innings not in (1, 2):
            audit["super_over_rows_excluded"] += len(rows)
            continue
        if m["format"] == "Other":
            audit["other_competition_rows_excluded"] += len(rows)
            continue
        if m["revised"]:
            audit["revised_match_rows_excluded"] += len(rows)
            continue
        over_counts = Counter(number(r["overid"]) for r in rows if r["extras_type"] in LEGAL)
        illegal_overs = [o for o, n in over_counts.items() if n > 6 or o < 1 or o > 20]
        numbers = [number(r["innings_ball_num"]) for r in rows]
        gaps = numbers != list(range(1, len(rows) + 1))
        if illegal_overs or gaps:
            quarantine.append({"match_id": mid, "innings": innings, "reason": "Over has >6 legal balls or invalid over" if illegal_overs else "Delivery sequence gap"})
            audit["quarantined_rows"] += len(rows)
            continue
        legal_count, wickets = 0, 0
        falls = []
        timeline = []
        knockout = m["stage"] in {"Final", "Semi Final", "Qualifier", "Eliminator"}
        for r in rows:
            over = number(r["overid"])
            recent = sum(legal_count - at < 12 for at in falls)
            score, why = pressure(over, wickets, recent, knockout)
            is_legal = r["extras_type"] in LEGAL
            striker, bowler = number(r["striker_id"]), number(r["bowler_id"])
            dismissed = number(r["dismissed_player_id"])
            wicket = truth(r["is_wicket"])
            dismissal = r["dismissal_type"]
            runs = number(r["runs"])
            striker_out, bowler_wicket = dismissal_flags(wicket, dismissed, striker, dismissal)
            for pid, name, bat, bowl in [(striker, r["striker_name"], r["batting_type"], ""), (bowler, r["bowler_name"], "", r["bowling_type"])]:
                if pid not in players:
                    players[pid] = {"name": name, "teams": [], "batting_style": "", "bowling_style": ""}
                if bat:
                    players[pid]["batting_style"] = bat
                if bowl:
                    players[pid]["bowling_style"] = bowl
            if wicket and not dismissed:
                audit["wickets_missing_dismissed_player"] += 1
            if wicket and dismissed and dismissed != striker:
                audit["non_striker_dismissals_not_charged_to_striker"] += 1
            timeline.append([f"{over-1}.{r['over_ball_num']}", score, wickets, runs, striker, bowler, int(wicket), int(is_legal), r["extras_type"], "; ".join(why)])
            if is_legal:
                batting_order = number(r["batting_order"])
                bat_role = "Top order" if batting_order <= 3 else "Middle order" if batting_order <= 7 else "Lower order"
                event = {"match": mid, "innings": innings, "format": m["format"], "year": m["date"][:4],
                         "phase": phase(over), "bat_role": bat_role, "style": r["pace_or_spin"] or "Unknown",
                         "striker": striker, "bowler": bowler, "runs": runs,
                         "out": striker_out,
                         "bw": bowler_wicket,
                         "boundary": int(truth(r["is_four"]) or truth(r["is_six"])), "pressure": score,
                         "collapse": (over <= 10 and wickets >= 3) or (10 < over <= 15 and wickets >= 4),
                         "cluster": recent >= 2, "knockout": knockout,
                         "side": r.get("on_or_off", ""), "stroke": r.get("stroke", ""),
                         "delivery": r.get("delivery_style", ""), "hand": r.get("batting_type", ""),
                         "bowling_type": r.get("bowling_type", "")}
                events.append(event)
                context_counts["high" if score >= THRESHOLD else "ordinary"] += 1
                if (mid, striker) not in xi_members or (mid, bowler) not in xi_members:
                    audit["legal_rows_with_xi_mapping_mismatch"] += 1
                legal_count += 1
            else:
                audit["non_legal_or_ambiguous_rows_excluded"] += 1
            if wicket:
                wickets += 1
                falls.append(legal_count)
        timelines.setdefault(mid, {"meta": m, "innings": {}})["innings"][innings] = timeline
    print(f"Context adjustment for {len(events):,} legal deliveries...", flush=True)
    attach_context(events)
    match_index = []
    output_dir.mkdir(parents=True, exist_ok=True)
    for mid, timeline in timelines.items():
        m = timeline["meta"]
        high = sum(p[1] >= THRESHOLD and p[7] for points in timeline["innings"].values() for p in points)
        match_index.append({**{k: v for k, v in m.items() if k != "revised"}, "pressure_balls": high})
        json_write(output_dir / "matches" / f"{mid}.json", timeline)
    match_index.sort(key=lambda m: (m["date"], m["id"]), reverse=True)
    results = {}
    excluded_output = {}
    for scope in ("Combined", "IPL", "T20I"):
        results[scope], excluded_output[scope] = {}, {}
        for role in ("batters", "bowlers"):
            print(f"Ranking {scope} {role}...", flush=True)
            ranked, excluded = rank(events, players, role, scope, detail=True)
            strict, _ = rank(events, players, role, scope, threshold=65)
            relaxed, _ = rank(events, players, role, scope, threshold=50)
            dropped, _ = rank(events, players, role, scope, drop_best=True)
            alternate1 = score_rows([dict(r) for r in ranked], (.6, .2, .2))
            alternate2 = score_rows([dict(r) for r in ranked], (.4, .4, .2))
            variants = [{r["id"]: r["rank"] for r in rows} for rows in (strict, relaxed, dropped, alternate1, alternate2)]
            for r in ranked:
                positions = [v[r["id"]] for v in variants if r["id"] in v]
                r["sensitivity"] = [min([r["rank"]] + positions), max([r["rank"]] + positions)]
                r["sensitivity_missing"] = len(variants) - len(positions)
                r["scenario_ranks"] = dict(zip(["Stricter pressure", "Broader pressure", "Best match removed", "Performance emphasis", "Uplift emphasis"], [v.get(r["id"]) for v in variants]))
                r["reasons"], r["limitation"] = reasons_for(r, role)
                r["consistency_pct"] = round(100 * r["consistency"], 2)
            results[scope][role] = ranked
            excluded_output[scope][role] = excluded
    from .player_details import build_player_details
    details = build_player_details(events, meta)
    # Only selectable players need the expanded payload; keep startup and repository size small.
    for scope in results:
        for role, ranked in results[scope].items():
            eligible = {str(r["id"]) for r in ranked}
            details[scope][role] = {pid: value for pid, value in details[scope][role].items() if pid in eligible}
    json_write(output_dir / "player_details.json", details)
    from .intelligence import build_intelligence
    insights, simulation = build_intelligence(events, players, results)
    for scope, scope_data in insights['scopes'].items():
        for role in ('batters', 'bowlers'):
            for pid, profile in scope_data[role].items():
                json_write(output_dir / 'insights' / scope / role / (pid + '.json'), profile)
    json_write(output_dir / "player_insights.json", {'meta':insights['meta'],
        'scopes':{s:{'audit':v['audit']} for s,v in insights['scopes'].items()}})
    json_write(output_dir / "simulation_data.json", simulation)
    valid_mids = {e["match"] for e in events}
    manifest = {name: {"sha256": hashlib.sha256((raw_dir / name).read_bytes()).hexdigest(), "bytes": (raw_dir / name).stat().st_size} for name in required}
    meta_output = {
        "version": "1.0.0", "built_at": datetime.now(timezone.utc).isoformat(),
        "source_rows": source_rows, "source_matches": len(matches), "analysed_matches": len(valid_mids),
        "legal_balls": len(events), "pressure_balls": context_counts["high"],
        "date_from": min(meta[mid]["date"] for mid in valid_mids), "date_to": max(meta[mid]["date"] for mid in valid_mids),
        "years": sorted({e["year"] for e in events}), "threshold": THRESHOLD,
        "min_balls": MIN_BALLS, "min_matches": MIN_MATCHES, "prior_balls": PRIOR_BALLS,
        "audit": dict(audit), "quarantined_innings": quarantine,
        "extras_codes": {k: dict(v) for k, v in extras.items()}, "sources": manifest,
        "limitations": [
            "extras1_runs maps to extras-type codes, including 6 on ordinary deliveries. It is not summed as runs. extras_2_runs is undocumented and not interpreted as an amount.",
            "Exact team totals, chase targets, required run rate, official strike rate and official bowling economy are not claimed.",
            "Pressure is a shared phase/wicket situation proxy, not a psychological measure or calibrated win probability. One-sided death overs can still be marked high pressure; a batting collapse may favour the bowler.",
            "Legal-ball batting strike rate excludes no-balls. Bat runs per six legal balls excludes all extras. Striker-dismissal rate excludes non-striker runouts and non-playing dismissals.",
            "Peer groups adjust for format, phase, innings and where supported year and batting position/bowling type. Opponent strength, exact venue effects, dew and pitch quality are not adjusted.",
            "Context expectations use the full supplied sample. These are descriptive historical rankings, not out-of-sample predictions.",
            "Reduced/revised matches, super overs, other T20 competitions, ambiguous/non-legal deliveries and malformed innings are excluded as documented in the audit.",
            "Scenario rank ranges measure sensitivity, not statistical confidence intervals. Eligibility and peer populations may change between scenarios.",
            "Dates and identities are accepted from the supplied pack without external verification; no current-form or squad-availability claim is made."
        ]}
    json_write(output_dir / "dashboard.json", {"meta": meta_output, "rankings": results, "excluded": excluded_output,
                                                "matches": match_index, "players": players})
    json_write(ROOT / "reports" / "data_audit.json", meta_output)
    for role in ("batters", "bowlers"):
        with (ROOT / "reports" / f"top_10_{role}.csv").open("w", encoding="utf-8", newline="") as file:
            fields = ["rank", "player", "rating", "pressure_balls", "pressure_matches", "pressure_strike_rate", "bat_runs_per_six", "wickets_per_100", "ordinary_impact", "pressure_impact", "scenario_rank_min", "scenario_rank_max", "reason", "limitation"]
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            for r in results["Combined"][role][:10]:
                p = r["pressure"]
                writer.writerow(dict(zip(fields, [r["rank"], r["name"], round(r["score"], 2), p["balls"], r["pressure_matches"], p["sr"], p["run_rate"], p["wicket_rate"], r["normal"]["impact"], p["impact"], *r["sensitivity"], " ".join(r["reasons"]), r["limitation"]])))
    write_report(results, meta_output)
    print(f"Built {output_dir / 'dashboard.json'}", flush=True)
    for role in ("batters", "bowlers"):
        print(role.upper() + ": " + ", ".join(r["name"] for r in results["Combined"][role][:10]))


def write_report(results, meta):
    template = (ROOT / "docs" / "methodology_template.md").read_text(encoding="utf-8")
    lines = [template, "\n## Dataset coverage\n",
             f"The supplied pack contains {meta['source_rows']:,} delivery rows and {meta['source_matches']} match records. The analysis retains {meta['legal_balls']:,} legal deliveries in {meta['analysed_matches']} matches, from {meta['date_from']} to {meta['date_to']}. {meta['pressure_balls']:,} retained deliveries meet the default pressure threshold.\n",
             "## Final combined rankings\n"]
    for role in ("batters", "bowlers"):
        lines.extend([f"### Top 10 {role}\n", "| Rank | Player | Rating | Pressure balls | Pressure matches | Scenario rank range |", "|---|---|---|---|---|---|"])
        for r in results["Combined"][role][:10]:
            lines.append(f"| {r['rank']} | {r['name']} | {r['score']:.2f} | {r['pressure']['balls']} | {r['pressure_matches']} | {r['sensitivity'][0]}–{r['sensitivity'][1]} |")
        for r in results["Combined"][role][:10]:
            lines.extend([f"\n#### {r['rank']}. {r['name']}\n", " ".join(r["reasons"]), "\nLimitation: " + r["limitation"]])
    lines.append("\n## Audit counts\n")
    lines.extend(f"- {key.replace('_', ' ')}: {value:,}" for key, value in meta["audit"].items())
    lines.append("\n## Limitations\n")
    lines.extend(f"- {value}" for value in meta["limitations"])
    lines.extend(["\n## Reproduce\n", "Run `python -m analysis.build --data-dir data/raw` from the project root. Run `python -m unittest discover -s tests -v` for the calculation checks. Source SHA-256 hashes are recorded in `reports/data_audit.json`. No random seed is needed: the pipeline is deterministic apart from its build timestamp.\n"])
    report = "\n".join(lines)
    (ROOT / "reports" / "METHODOLOGY.md").write_text(report, encoding="utf-8")
    (ROOT / "web" / "data" / "METHODOLOGY.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data" / "raw")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "web" / "data")
    args = parser.parse_args()
    build(args.data_dir.resolve(), args.output_dir.resolve())
