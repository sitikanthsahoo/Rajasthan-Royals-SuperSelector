"""Meaningful boundary and source-output checks; run with Python's built-in unittest."""
import json
import math
import unittest
from pathlib import Path

from analysis.build import (LEGAL, accumulator, add, attach_context, components,
                            dismissal_flags, percentile, pressure, rank, summary)

ROOT = Path(__file__).resolve().parents[1]


def event(**kwargs):
    base = dict(format="IPL", phase="Middle", innings=1, year="2025", bat_role="Middle order",
                style="Spin", runs=1, out=0, bw=0, boundary=0, match=1, striker=1, bowler=2,
                pressure=60, au=.1, bu=-.1, ae=(1.2,.05), be=(1.2,.05))
    base.update(kwargs)
    return base


class CricketRulesTest(unittest.TestCase):
    def test_death_starts_at_sixteenth_over(self):
        self.assertEqual(pressure(15,0,0)[0],20)
        self.assertEqual(pressure(16,0,0)[0],60)
        self.assertEqual(pressure(19,0,0)[0],75)

    def test_collapse_and_score_cap(self):
        self.assertEqual(pressure(5,3,2)[0],60)
        self.assertEqual(pressure(12,4,2)[0],60)
        self.assertEqual(pressure(20,7,2,True)[0],100)

    def test_no_future_delivery_inputs(self):
        # The API cannot consume current-ball runs, wicket, match result or a final score.
        import inspect
        self.assertEqual(list(inspect.signature(pressure).parameters),['over','wickets','recent_wickets','knockout'])
        self.assertLess(pressure(5,2,1)[0],pressure(5,3,2)[0])

    def test_runout_is_not_bowler_wicket(self):
        self.assertEqual(dismissal_flags(True,1,1,'RunOut'),(1,0))
        self.assertEqual(dismissal_flags(True,3,1,'RunOut'),(0,0))
        self.assertEqual(dismissal_flags(True,1,1,'Caught'),(1,1))
        self.assertEqual(dismissal_flags(True,1,1,'Retire Out'),(0,0))

    def test_legal_ball_definition(self):
        self.assertTrue({'None','byes','legbyes'} <= LEGAL)
        self.assertTrue({'wide','Overstep','other','Penalty'}.isdisjoint(LEGAL))

    def test_rates_do_not_include_extras_codes(self):
        a=accumulator()
        for runs in [0,4,1,0,6,1]:
            add(a,event(runs=runs,boundary=int(runs in (4,6))), 'batters')
        s=summary(a)
        self.assertEqual(s['balls'],6)
        self.assertEqual(s['runs'],12)
        self.assertEqual(s['sr'],200)
        self.assertEqual(s['run_rate'],12)
        self.assertEqual(s['boundary_pct'],33.33)


class RankingTest(unittest.TestCase):
    def test_context_impact_conserves_mean(self):
        events=[event(runs=i%7,out=int(i%17==0),bw=int(i%17==0)) for i in range(210)]
        attach_context(events)
        self.assertAlmostEqual(sum(e['au'] for e in events),0,places=10)
        self.assertAlmostEqual(sum(e['bu'] for e in events),0,places=10)
        high=[e for e in events if e['runs']==6 and not e['out']][0]
        self.assertGreater(high['au'],0)
        self.assertLess(high['bu'],0)

    def test_midrank_ties(self):
        self.assertEqual(percentile([1,1,1],1),50)
        self.assertEqual(percentile([1,2,3],2),50)
        self.assertEqual(percentile([1,2,2,3],2),50)

    def test_shrinkage_reduces_small_samples(self):
        normal=accumulator();normal.update(balls=100,utility=0)
        small=accumulator();small.update(balls=60,utility=6)
        large=accumulator();large.update(balls=600,utility=60)
        self.assertLess(components(small,normal,{})['quality'],components(large,normal,{})['quality'])

    def test_match_gate_prevents_one_match_star(self):
        players={1:dict(name='Sample Batter',teams=[],batting_style='RHB',bowling_style='')}
        one_match=[event(match=1) for _ in range(72)] + [event(pressure=10) for _ in range(60)]
        rankings,excluded=rank(one_match,players,'batters')
        self.assertEqual(rankings,[])
        self.assertIn('8 pressure matches',excluded[0]['reason'])
        spread=[event(match=i//9+1) for i in range(72)] + [event(pressure=10) for _ in range(60)]
        rankings,_=rank(spread,players,'batters')
        self.assertEqual(len(rankings),1)
        self.assertEqual(rankings[0]['pressure_matches'],8)

    def test_fewer_than_six_balls_not_consistent_match(self):
        p=accumulator();p.update(balls=100,utility=10)
        n=accumulator();n.update(balls=100,utility=0)
        m=accumulator();m.update(balls=5,utility=3)
        self.assertEqual(components(p,n,{1:m})['pressure_matches'],0)


class GeneratedOutputTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path=ROOT/'web'/'data'/'dashboard.json'
        if not path.exists():
            raise unittest.SkipTest('Run analysis.build before checking generated outputs')
        cls.data=json.loads(path.read_text(encoding='utf-8'))

    def test_all_lists_ordered_unique_finite_and_eligible(self):
        for scope,roles in self.data['rankings'].items():
            for role,rows in roles.items():
                self.assertGreaterEqual(len(rows),10,(scope,role))
                self.assertEqual(len({r['id'] for r in rows}),len(rows))
                self.assertEqual([r['rank'] for r in rows],list(range(1,len(rows)+1)))
                self.assertEqual([r['score'] for r in rows],sorted([r['score'] for r in rows],reverse=True))
                for r in rows:
                    self.assertTrue(math.isfinite(r['score']))
                    self.assertGreaterEqual(r['pressure']['balls'],60)
                    self.assertGreaterEqual(r['normal']['balls'],60)
                    self.assertGreaterEqual(r['pressure_matches'],8)
                    weighted=.5*r['components']['quality']+.3*r['components']['uplift']+.2*r['components']['consistency']
                    self.assertAlmostEqual(r['score'],weighted,places=3)

    def test_source_rows_reconcile(self):
        m=self.data['meta'];audit=m['audit']
        mutually_exclusive=['super_over_rows_excluded','other_competition_rows_excluded','revised_match_rows_excluded','quarantined_rows','non_legal_or_ambiguous_rows_excluded','missing_match_metadata_rows','duplicate_delivery_keys']
        self.assertEqual(m['source_rows'],m['legal_balls']+sum(audit.get(k,0) for k in mutually_exclusive))

    def test_every_match_detail_exists_and_pressure_is_pre_delivery(self):
        count=0;high=0
        for m in self.data['matches']:
            data=json.loads((ROOT/'web'/'data'/'matches'/f"{m['id']}.json").read_text(encoding='utf-8'))
            for points in data['innings'].values():
                wickets=0
                for p in points:
                    self.assertEqual(p[2],wickets)
                    self.assertTrue(0<=p[1]<=100)
                    wickets+=p[6]
                    count+=p[7]
                    high+=int(bool(p[7]) and p[1]>=55)
        self.assertEqual(count,self.data['meta']['legal_balls'])
        self.assertEqual(high,self.data['meta']['pressure_balls'])

    def test_report_contains_same_twenty_selections(self):
        report=(ROOT/'reports'/'METHODOLOGY.md').read_text(encoding='utf-8')
        for role in ('batters','bowlers'):
            for r in self.data['rankings']['Combined'][role][:10]:
                self.assertIn(f"| {r['rank']} | {r['name']} | {r['score']:.2f} |",report)


if __name__=='__main__':
    unittest.main()
