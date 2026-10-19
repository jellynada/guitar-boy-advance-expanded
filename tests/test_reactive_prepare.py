import json
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from tools.reactive_prepare import convert_reactive,synthetic_reactive
from tools.audio_prepare import RATE,PRE_ROLL
from tools.chart_importer import normalize
from test_audio_prepare import wav

class ReactiveTests(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def test_duration_origin_headroom_determinism(self):
        g=self.root/'g.wav';b=self.root/'b.wav';wav(g,800);wav(b,1600)
        a=convert_reactive([g],[b],self.root/'a');c=convert_reactive([g],[b],self.root/'c')
        self.assertEqual(a,c);self.assertEqual(a['source_samples'],3277);self.assertEqual(a['schema_version'],'gba-reactive-audio-v1')
        x=(self.root/'a/imported_audio.bin').read_bytes();y=(self.root/'a/imported_backing.bin').read_bytes()
        self.assertEqual(len(x),len(y));self.assertEqual(x[:PRE_ROLL],bytes(PRE_ROLL));self.assertFalse(any(x[PRE_ROLL+1639:]))
        signed=lambda n:n if n<128 else n-256
        self.assertLessEqual(max(abs(signed(p))+abs(signed(q)) for p,q in zip(x,y)),127)
    def test_role_selection_invalid(self):
        g=self.root/'g.wav';wav(g)
        for guitar,back in [([],[g]),([g],[]),([g],[g]),([g,g],[g])]:
            with self.assertRaises(ValueError):convert_reactive(guitar,back,self.root/'a')
    def test_fixture_distinct_tracks(self):
        song=normalize(Path('tests/fixtures/runtime/easy.chart').read_text());r=synthetic_reactive(song,self.root)
        a=(self.root/'imported_audio.bin').read_bytes();b=(self.root/'imported_backing.bin').read_bytes()
        self.assertNotEqual(a,b);self.assertEqual(len(a),len(b));self.assertTrue(r['synthetic'])
        self.assertTrue(any(a[PRE_ROLL:PRE_ROLL+1000]));self.assertTrue(any(b[PRE_ROLL:PRE_ROLL+1000]))
    def test_build_rejects_corrupt_backing_and_unsafe_mix(self):
        song=normalize(Path('tests/fixtures/runtime/easy.chart').read_text());synthetic_reactive(song,self.root/'pcm')
        out=self.root/'build';out.mkdir();(out/'imported_chart.hpp').write_text('{33554432ULL,0,0}')
        command=[sys.executable,'tools/build_audio.py','--output-dir',str(out),'--audio-dir',str(self.root/'pcm')]
        self.assertEqual(subprocess.run(command,capture_output=True).returncode,0)
        (self.root/'pcm/imported_backing.bin').write_bytes(b'broken');self.assertNotEqual(subprocess.run(command,capture_output=True).returncode,0)
        synthetic_reactive(song,self.root/'pcm')
        for name in ['imported_audio.bin','imported_backing.bin']:
            data=bytearray((self.root/'pcm'/name).read_bytes());data[PRE_ROLL]=100;(self.root/'pcm'/name).write_bytes(data)
        manifest=json.loads((self.root/'pcm/audio.json').read_text());manifest['pcm_sha256']=hashlib.sha256((self.root/'pcm/imported_audio.bin').read_bytes()).hexdigest();manifest['backing_sha256']=hashlib.sha256((self.root/'pcm/imported_backing.bin').read_bytes()).hexdigest();(self.root/'pcm/audio.json').write_text(json.dumps(manifest))
        self.assertNotEqual(subprocess.run(command,capture_output=True).returncode,0)
    def test_package_reactive_and_cleanup(self):
        p=self.root/'package';p.mkdir();(p/'notes.chart').write_text('[Song]\n{\nResolution = 192\n}\n[SyncTrack]\n{\n0 = B 120000\n}\n[EasySingle]\n{\n0 = N 0 1\n}\n')
        wav(p/'guitar.wav',8000);wav(p/'song.wav',8000)
        out=self.root/'out';cmd=[sys.executable,'tools/prepare_song.py',str(p),'--reactive','--guitar-stem','guitar','--backing-stem','song','--output-dir',str(out)]
        r=subprocess.run(cmd,capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        self.assertEqual(json.loads((out/'audio/audio.json').read_text())['schema_version'],'gba-reactive-audio-v1')
        cmd[7]='preview';self.assertNotEqual(subprocess.run(cmd,capture_output=True).returncode,0)
        self.assertFalse((out/'audio/imported_backing.bin').exists());self.assertFalse((out/'imported_chart.hpp').exists())
if __name__=='__main__':unittest.main()
