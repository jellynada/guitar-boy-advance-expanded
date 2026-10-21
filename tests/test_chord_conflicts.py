import copy,unittest
from tools.report_chord_conflicts import report

def note(lane,start,end):
    return dict(lane=lane,tick=start,duration_ticks=192 if end>start else 0,duration_us=end-start,start_us=start,end_us=end)
def song(difficulty,notes):
    return dict(resolution=192,tracks=[dict(difficulty=difficulty,instrument='five_fret_lead_guitar',notes=notes)])
class ConflictReportTests(unittest.TestCase):
    def test_chords_are_reported_without_modifying_source(self):
        source=song('Medium',[note(0,100,300),note(1,100,300),note(3,400,400)]);before=copy.deepcopy(source);chart=report(source)['charts'][0]
        self.assertEqual(source,before);self.assertEqual(len(chart['simultaneous_opposing_chords']),1)
        row=chart['simultaneous_opposing_chords'][0];self.assertEqual(row['runtime_us'],2000100);self.assertEqual([n['button']for n in row['heads']],['LEFT','RIGHT'])
    def test_hard_uses_right_lane_two_and_reports_hold_interaction(self):
        chart=report(song('Hard',[note(0,100,400),note(2,200,200)]))['charts'][0]
        self.assertEqual(len(chart['simultaneous_opposing_chords']),0);self.assertEqual(len(chart['opposing_hold_interactions']),1)
        self.assertEqual(chart['opposing_hold_interactions'][0]['held'][0]['end_us'],400)
    def test_release_boundary_is_not_an_overlapping_hold(self):
        chart=report(song('Medium',[note(0,100,200),note(1,200,200)]))['charts'][0]
        self.assertFalse(chart['opposing_hold_interactions']);self.assertFalse(chart['simultaneous_opposing_chords'])
