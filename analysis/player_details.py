"""Descriptive player-lab evidence. Never changes ranking inputs or scores."""
from collections import defaultdict

def situation_keys(e):
    result=[]
    if e['phase']=='Death':result.append('Death overs')
    if e.get('collapse'):result.append('Wicket-loss situation')
    if e.get('cluster'):result.append('Two recent wickets')
    if e.get('knockout'):result.append('Knockout match')
    return result

def build_player_details(events, metadata):
    from .build import accumulator, add, summary
    def record():return {'all':accumulator(),'matches':defaultdict(lambda:{'all':accumulator(),'pressure':accumulator(),'situations':defaultdict(accumulator)}),'situations':defaultdict(accumulator)}
    result={}
    for scope in ('Combined','IPL','T20I'):
        result[scope]={}
        for role in ('batters','bowlers'):
            records=defaultdict(record)
            for e in events:
                if scope!='Combined' and e['format']!=scope:continue
                pid=e['striker' if role=='batters' else 'bowler'];rec=records[pid]
                add(rec['all'],e,role);add(rec['matches'][e['match']]['all'],e,role)
                if e['pressure']>=55:
                    add(rec['matches'][e['match']]['pressure'],e,role)
                    for key in situation_keys(e):
                        add(rec['situations'][key],e,role)
                        add(rec['matches'][e['match']]['situations'][key],e,role)
            def stats(a):
                return {**summary(a),'sample_average':round(a['runs']/a['wickets'],2) if a['wickets'] else None,'bowling_strike_rate':round(a['balls']/a['wickets'],2) if a['wickets'] else None}
            result[scope][role]={str(pid):{'overall':stats(r['all']),
                'recent':[{'match_id':mid,'date':metadata[mid]['date'],'teams':metadata[mid]['home']+' vs '+metadata[mid]['away'],'all':stats(a['all']),'pressure':stats(a['pressure']),'situations':{k:stats(v) for k,v in a['situations'].items()}} for mid,a in sorted(r['matches'].items(),key=lambda x:(metadata[x[0]]['date'],x[0]),reverse=True)[:8]],
                'situations':[{'name':name,**stats(a)} for name,a in r['situations'].items()]} for pid,r in records.items()}
    return result
