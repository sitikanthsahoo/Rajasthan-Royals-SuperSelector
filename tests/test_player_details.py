import unittest
from analysis.player_details import build_player_details, situation_keys
from tests.test_analysis import event

class PlayerDetailsTest(unittest.TestCase):
    def test_recent_is_chronological_and_includes_zero_pressure(self):
        meta={1:{'date':'2026-01-02','home':'A','away':'B'},2:{'date':'2026-01-01','home':'C','away':'D'}}
        rows=[event(match=1,pressure=20,runs=4),event(match=2,pressure=60,runs=2,out=1)]
        d=build_player_details(rows,meta)['Combined']['batters']['1']
        self.assertEqual([m['match_id'] for m in d['recent']],[1,2])
        self.assertEqual(d['recent'][0]['pressure']['balls'],0)
        self.assertIsNone(d['recent'][0]['pressure']['sr'])
        self.assertEqual(d['overall']['sample_average'],6)
        self.assertIsNone(d['recent'][0]['all']['sample_average'])

    def test_scope_and_overlapping_situations(self):
        e=event(phase='Death',cluster=True,knockout=True,runs=6)
        self.assertEqual(situation_keys(e),['Death overs','Two recent wickets','Knockout match'])
        d=build_player_details([e],{1:{'date':'2026-01-01','home':'A','away':'B'}})
        self.assertEqual(d['T20I']['batters'],{})
        self.assertEqual(len(d['IPL']['batters']['1']['situations']),3)
        self.assertEqual(d['IPL']['batters']['1']['overall']['balls'],1)
        self.assertIsNone(d['IPL']['bowlers']['2']['overall']['sample_average'])
