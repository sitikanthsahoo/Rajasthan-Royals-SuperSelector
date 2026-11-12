"""Descriptive scouting cuts and empirical scenario counts; never alters rankings."""
from collections import Counter, defaultdict

PHASES = ('All', 'Powerplay', 'Middle', 'Death')

def bowling_group(style):
    s = (style or '').lower()
    if 'chinaman' in s or ('left' in s and 'wrist' in s): return 'Left-arm wrist spin'
    if 'orthodox' in s: return 'Left-arm orthodox'
    if 'leg' in s: return 'Leg spin'
    if 'off' in s: return 'Off spin'
    if 'left' in s: return 'Left-arm pace'
    if 'right' in s: return 'Right-arm pace'
    return 'Unknown'

def blank_stats():
    return {'balls':0, 'runs':0, 'wickets':0, 'dots':0, 'boundaries':0, '_matches':set()}

def add_stats(a, e, role):
    a['balls'] += 1; a['runs'] += e['runs']
    a['wickets'] += e['out'] if role == 'batters' else e['bw']
    a['dots'] += int(e['runs'] == 0); a['boundaries'] += e['boundary']
    a['_matches'].add(e['match'])

def finish(a):
    n = a['balls']
    return {k:v for k,v in a.items() if k != '_matches'} | {
        'matches':len(a['_matches']), 'sr':round(100*a['runs']/n,2) if n else None,
        'rate':round(6*a['runs']/n,2) if n else None,
        'wicket_rate':round(100*a['wickets']/n,2) if n else None,
        'dot_pct':round(100*a['dots']/n,2) if n else None,
        'boundary_pct':round(100*a['boundaries']/n,2) if n else None}

def blank_cut():
    return {'total':blank_stats(), **{key:defaultdict(blank_stats) for key in
        ('sides','shots','styles','hands','deliveries','opponents','side_hand')}}

def outcome_index(e):
    # 0..6 runs in each of: no striker wicket, credited striker wicket, other striker dismissal.
    status = 1 if e['out'] and e['bw'] else 2 if e['out'] else 0
    return status*7 + e['runs']

def histogram(): return [0]*21
def model_player(): return {'contexts':defaultdict(histogram), 'versus':defaultdict(histogram)}

def build_intelligence(events, players, rankings):
    insights = {'meta':{'source':'Supplied CSV pack; retained legal deliveries',
        'checked':'2026-11-12', 'field_note':'Side tags are supplied annotations, not tracked shot coordinates. Shot names and side labels can disagree; no exact wagon-wheel angle is inferred.',
        'min_balls':30, 'min_matches':3}, 'scopes':{}}
    model = {'version':1, 'meta':{'source':'Same retained legal-ball sample as rankings',
        'runs':'bat runs only; extras and non-striker dismissals are not simulated',
        'prior_balls':60, 'pair_prior_balls':120, 'validated_forecast':False,
        'date_from':min(e['year'] for e in events), 'date_to':max(e['year'] for e in events)}, 'scopes':{}}
    for scope in ('Combined','IPL','T20I'):
        selected = {role:{r['id'] for r in rankings[scope][role]} for role in ('batters','bowlers')}
        cuts = {role:defaultdict(lambda:defaultdict(blank_cut)) for role in selected}
        league = defaultdict(histogram)
        batters, bowlers = defaultdict(model_player), defaultdict(model_player)
        pairs = defaultdict(lambda:defaultdict(histogram))
        hands, styles = defaultdict(Counter), defaultdict(Counter)
        audit = Counter()
        for e in events:
            if scope != 'Combined' and e['format'] != scope: continue
            audit['retained_balls'] += 1
            side = e.get('side') if e.get('side') in ('Off-side','On-side') else 'Unknown'
            hand = e.get('hand') if e.get('hand') in ('RHB','LHB') else 'Unknown'
            group = bowling_group(e.get('bowling_type'))
            audit['side_tagged_balls'] += int(side != 'Unknown')
            audit['stroke_tagged_balls'] += int(e.get('stroke','') not in ('','None'))
            for role, pid, opponent in (('batters',e['striker'],e['bowler']),('bowlers',e['bowler'],e['striker'])):
                if pid not in selected[role]: continue
                for phase in ('All',e['phase']):
                    cut = cuts[role][pid][phase]; add_stats(cut['total'],e,role)
                    for key, value in [('sides',side),('shots',e.get('stroke') or 'Unknown'),
                        ('styles',group),('hands',hand),('deliveries',e.get('delivery') or 'Unknown'),
                        ('opponents',str(opponent)),('side_hand',hand+'|'+side)]:
                        add_stats(cut[key][value],e,role)
            if not 0 <= e['runs'] <= 6:
                audit['unsupported_simulation_runs'] += 1; continue
            idx = outcome_index(e)
            context = e['phase']+'|'+('H' if e['pressure'] >= 55 else 'L')
            keys = ('All',e['phase'],context)
            for key in keys: league[key][idx] += 1
            bid, wid = e['striker'],e['bowler']
            if bid in selected['batters']:
                hands[bid][hand] += 1
                for key in keys:
                    batters[bid]['contexts'][key][idx] += 1
                    batters[bid]['versus'][key+'|'+group][idx] += 1
            if wid in selected['bowlers']:
                styles[wid][group] += 1
                for key in keys:
                    bowlers[wid]['contexts'][key][idx] += 1
                    bowlers[wid]['versus'][key+'|'+hand][idx] += 1
            if bid in selected['batters'] and wid in selected['bowlers']:
                for key in keys: pairs[f'{bid}:{wid}'][key][idx] += 1
        result = {}
        for role, profiles in cuts.items():
            result[role] = {}
            for pid, phases in profiles.items():
                final = {}
                for phase, cut in phases.items():
                    final[phase] = {'total':finish(cut['total'])}
                    for key, groups in cut.items():
                        if key == 'total': continue
                        entries = [{'name':name, **finish(stats)} for name,stats in groups.items()]
                        if key == 'opponents':
                            for row in entries:
                                row['id'] = int(row['name']); row['name'] = players.get(row['id'],{}).get('name','Unknown')
                            entries = sorted(entries,key=lambda x:(-x['balls'],x['id']))[:12]
                        final[phase][key] = sorted(entries,key=lambda x:(-x['balls'],x['name']))
                result[role][str(pid)] = final
        insights['scopes'][scope] = {**result, 'audit':dict(audit)}
        for pid, p in batters.items(): p['hand'] = hands[pid].most_common(1)[0][0]
        for pid, p in bowlers.items(): p['style'] = styles[pid].most_common(1)[0][0]
        model['scopes'][scope] = {'league':dict(league),'batters':dict(batters),'bowlers':dict(bowlers),'pairs':dict(pairs)}
    return insights, model
