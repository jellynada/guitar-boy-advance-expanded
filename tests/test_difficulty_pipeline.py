import json
from pathlib import Path
import tempfile
import unittest
from tools.generate_difficulty_example import generate_difficulties
from tools.song_pipeline import prepare, verify_prepared
from tools.adapt_chart import adapt
from tools.difficulty_data import LAYOUTS

class DifficultyPipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.source=generate_difficulties(self.root/'examples')

    def test_all_menu_charts_have_native_counts_and_owner_controls(self):
        m=prepare(self.source,self.root/'prepared',mix=['melody.wav'],difficulty='All')
        self.assertEqual(m['schema_version'],'gba-prepared-song-v2')
        self.assertEqual([(d['name'],d['note_heads']) for d in m['runtime']['difficulties']],[('Easy',6),('Medium',10),('Hard',13)])
        self.assertEqual(m['runtime']['difficulties'][2]['physical_controls'],['LEFT','UP/DOWN','RIGHT','B','A'])
        self.assertEqual(verify_prepared(self.root/'prepared'),m)
        text=(self.root/'prepared/imported_chart.hpp').read_text()
        self.assertIn('imported_note_count = 13;',text)
        self.assertIn('imported_choices[]',text)

    def test_each_native_difficulty_can_be_prepared(self):
        for difficulty,count in [('Easy',6),('Medium',10),('Hard',13)]:
            m=prepare(self.source,self.root/difficulty,mix=['melody.wav'],difficulty=difficulty)
            self.assertEqual(m['runtime']['note_heads'],count)
            self.assertEqual(m['runtime']['physical_controls'],LAYOUTS[difficulty])
            verify_prepared(self.root/difficulty)

    def test_expert_is_not_relabelled_hard(self):
        prepare(self.source,self.root/'data',mix=['melody.wav'])
        song=json.loads((self.root/'data/normalized-song.json').read_text())
        with self.assertRaises(ValueError):adapt(song,difficulty='Expert',instrument='five_fret_lead_guitar')

    def test_unsupported_medium_lane_is_not_dropped(self):
        chart=self.source/'notes.chart';s=chart.read_text();start=s.index('[MediumSingle]')
        chart.write_text(s[:start]+s[start:].replace('0 = N 0 1','0 = N 4 1',1))
        with self.assertRaises(ValueError):prepare(self.source,self.root/'bad',mix=['melody.wav'],difficulty='All')
        self.assertFalse((self.root/'bad/song-manifest.json').exists())

if __name__=='__main__':unittest.main()
