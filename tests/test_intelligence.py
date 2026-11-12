import unittest
from analysis.intelligence import build_intelligence, bowling_group, outcome_index

def event(**kw):
    return dict(match=1,year='2026',format='IPL',striker=1,bowler=2,runs=4,out=0,bw=0,
        boundary=1,phase='Death',pressure=60,side='Off-side',stroke='Cover Drive',
        hand='RHB',bowling_type='Right-arm Fast',delivery='Yorker') | kw

class IntelligenceTest(unittest.TestCase):
    def build(self,events):
        rankings={s:{'batters':[{'id':1}],'bowlers':[{'id':2}]} for s in ('Combined','IPL','T20I')}
        return build_intelligence(events,{1:{'name':'Batter'},2:{'name':'Bowler'}},rankings)

    def test_field_unknowns_scope_and_role_dismissals(self):
        i,m=self.build([event(),event(runs=0,boundary=0,out=1,bw=0,side=''),event(format='T20I',runs=6,hand='LHB',side='On-side')])
        p=i['scopes']['IPL']['batters']['1']['All']
        self.assertEqual(p['total']['runs'],4)
        self.assertEqual(p['total']['wickets'],1)
        self.assertEqual(sum(x['balls'] for x in p['sides']),2)
        self.assertEqual(next(x for x in p['sides'] if x['name']=='Unknown')['balls'],1)
        self.assertEqual(i['scopes']['IPL']['bowlers']['2']['All']['total']['wickets'],0)
        self.assertEqual(m['scopes']['IPL']['pairs']['1:2']['All'][14],1)
        self.assertEqual(sum(m['scopes']['Combined']['league']['All']),3)
        self.assertEqual(sum(m['scopes']['T20I']['league']['All']),1)

    def test_joint_outcome_keeps_runs_and_credit(self):
        self.assertEqual(outcome_index(event(runs=1,out=1,bw=1)),8)
        self.assertEqual(outcome_index(event(runs=0,out=0,bw=0)),0)
        self.assertEqual(outcome_index(event(runs=2,out=1,bw=0)),16)

    def test_style_groups_and_sample_matches(self):
        self.assertEqual(bowling_group('Slow left-arm orthodox'),'Left-arm orthodox')
        self.assertEqual(bowling_group('Left-arm Chinaman'),'Left-arm wrist spin')
        self.assertEqual(bowling_group('Right-arm Leg-Break'),'Leg spin')
        i,_=self.build([event(match=1),event(match=2),event(match=2)])
        self.assertEqual(i['scopes']['IPL']['batters']['1']['Death']['total']['matches'],2)
        self.assertEqual(i['scopes']['IPL']['batters']['1']['Death']['styles'][0]['name'],'Right-arm pace')

if __name__=='__main__': unittest.main()
