import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import wave
from tools.compose_public_demo import generate, arrange, TITLE, COUNT, RATE
from tools.song_pipeline import prepare, verify_prepared


class DemoCompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.root=Path(cls.temp.name)
        cls.provenance=generate(cls.root/'source')
        cls.manifest=prepare(cls.root/'source',cls.root/'prepared',difficulty='All',guitar='guitar.wav',backing=['backing.wav'],max_duration=75,handheld=True,display_title=TITLE)
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def test_original_arrangement_is_pitched_and_rhythmic(self):
        events,charts=arrange();self.assertEqual({e['role']for e in events},{'guitar','bass','kick','snare','hat'})
        self.assertEqual(len({e['pitch']for e in events if e['role']=='guitar'}),15)
        guitar_onsets={e['tick']for e in events if e['role']=='guitar'}
        for notes in charts.values():self.assertTrue(all(t in guitar_onsets for t,l,d in notes))
    def test_immutable_source_and_separate_roles(self):
        for name in ['guitar.wav','backing.wav']:
            with wave.open(str(self.root/'source'/name))as w:self.assertEqual((w.getframerate(),w.getnchannels(),w.getnframes()),(RATE,1,COUNT))
        self.assertNotEqual(self.provenance['stems']['guitar.wav'],self.provenance['stems']['backing.wav'])
        self.assertEqual(self.provenance['source_seconds'],78.75)
    def test_75s_counts_controls_and_no_repairs(self):
        m=self.manifest;self.assertEqual([(c['name'],c['note_heads'])for c in m['runtime']['difficulties']],[('Easy',86),('Medium',171),('Hard',335)])
        self.assertEqual(m['runtime']['genuine_sustains_by_difficulty'],{'Easy':11,'Medium':11,'Hard':10})
        r=json.loads((self.root/'prepared/derivation-report.json').read_text())
        self.assertTrue(all(not c['adaptation']['changes'] and not c['adaptation']['after']['conflicts']for c in r['charts']))
        self.assertEqual(m['audio']['source_samples'],1228800);self.assertEqual(m['audio']['playback_samples'],1261568)
    def test_playable_triples_and_crossing_tails_retained(self):
        d=json.loads((self.root/'prepared/adapted.json').read_text());hard=d['charts'][2]
        groups={}
        for n in hard['notes']:groups.setdefault(n['start_us'],[]).append(n['lane'])
        self.assertIn([0,3,4],list(groups.values()))
        r=json.loads((self.root/'prepared/derivation-report.json').read_text())
        self.assertTrue(all(any(n['action']=='trim-hold'for n in c['provenance'])for c in r['charts']))
    def test_short_real_song_title_is_bound_and_verified(self):
        d=json.loads((self.root/'prepared/adapted.json').read_text());self.assertEqual(d['title'],TITLE);self.assertLessEqual(len(TITLE),16)
        self.assertEqual(verify_prepared(self.root/'prepared'),self.manifest)
    def test_regeneration_exact_and_different_from_beep_fixture(self):
        second=generate(self.root/'repeat');self.assertEqual(second,self.provenance)
        self.assertEqual((self.root/'repeat/notes.chart').read_bytes(),(self.root/'source/notes.chart').read_bytes())
        self.assertEqual(second['title'],'Copper Circuit')


if __name__=='__main__':unittest.main()

class DemoDeliveryBoundaryTests(unittest.TestCase):
    def test_reviewed_downloads_are_not_source_inputs(self):
        import subprocess
        from tools.release_common import source_snapshot
        with tempfile.TemporaryDirectory()as t:
            root=Path(t);(root/'README.md').write_text('fixture');d=root/'public-demo-downloads';d.mkdir()
            (d/'Guitar-Boy-Advance-Expanded-v0.1.0-alpha-RC1.gba').write_bytes(b'approved artifact canary')
            def git(*args):subprocess.run(['git','-C',str(root),*args],check=True,stdout=subprocess.DEVNULL)
            git('init','-q');git('add','.');git('-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','fixture')
            files,_=source_snapshot(root);self.assertEqual(set(files),{'README.md'})
            (d/'unreviewed-song.zip').write_bytes(b'private');git('add','.');git('-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','bad fixture')
            with self.assertRaisesRegex(ValueError,'Unreviewed public demo'):source_snapshot(root)
    def test_archive_checked_before_extraction(self):
        import zipfile
        from tools.verify_demo_zip import verify
        from tools.build_public_demo import ROM
        with tempfile.TemporaryDirectory()as t:
            root=Path(t);archive=root/'demo.zip';data=b'unit fixture ROM, not runnable'
            with zipfile.ZipFile(archive,'w')as z:z.writestr(ROM,data)
            receipt=dict(archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),rom_sha256=hashlib.sha256(data).hexdigest(),payload_sha256={ROM:hashlib.sha256(data).hexdigest()})
            r=root/'receipt.json';r.write_text(json.dumps(receipt));self.assertEqual(verify(archive,r,root/'good')['extraction'],'passed')
            archive.write_bytes(archive.read_bytes()+b'changed')
            with self.assertRaisesRegex(ValueError,'Archive checksum'):verify(archive,r,root/'bad')
            self.assertFalse((root/'bad').exists())
