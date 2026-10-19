import contextlib
import io
import json
import math
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import wave

from tools.audio_prepare import convert_files,decoder_version,synthetic_audio,RATE,PRE_ROLL,TAIL,GUARD
from tools.chart_importer import normalize


def wav(path,count=800,rate=8000):
    with wave.open(str(path),'wb') as out:
        out.setnchannels(1);out.setsampwidth(2);out.setframerate(rate)
        out.writeframes(b''.join(struct.pack('<h',int(12000*math.sin(i*440*2*math.pi/rate))) for i in range(count)))


class AudioTests(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()

    def test_wav_conversion_count_origin_headroom(self):
        path=self.root/'source.wav';wav(path,800)
        report=convert_files([path],self.root/'out')
        self.assertEqual(report['source_samples'],1639) # ceil(.1*16384), actual resampler endpoint
        raw=(self.root/'out/imported_audio.bin').read_bytes()
        self.assertEqual(raw[:PRE_ROLL],bytes(PRE_ROLL))
        self.assertFalse(any(raw[PRE_ROLL+report['source_samples']:]))
        self.assertLessEqual(report['output_peak'],108)
        self.assertEqual(report['playback_samples'],PRE_ROLL+1639+TAIL)
        self.assertGreaterEqual(len(raw),report['playback_samples']+GUARD)
        self.assertEqual(len(raw)%16,0)

    def test_lengths_determinism_and_zero_padding(self):
        a=self.root/'a.wav';b=self.root/'b.wav';wav(a,800);wav(b,1600)
        first=convert_files([a,b],self.root/'one')
        second=convert_files([a,b],self.root/'two')
        self.assertEqual(first,second)
        self.assertEqual((self.root/'one/imported_audio.bin').read_bytes(),(self.root/'two/imported_audio.bin').read_bytes())
        self.assertEqual(first['source_samples'],3277)
        self.assertEqual(len(first['sources']),2)
        self.assertIn('zero-pad',first['mix_rule'])

    def test_opus_decoder_preskip_duration(self):
        a=self.root/'test.wav';wav(a,8000)
        opus=self.root/'test.opus'
        subprocess.run(['ffmpeg','-v','error','-i',str(a),'-c:a','libopus',str(opus)],check=True)
        report=convert_files([opus],self.root/'out')
        self.assertEqual(report['sources'][0]['codec'],'opus')
        self.assertEqual(report['source_samples'],16384)
        self.assertLess(abs(report['source_duration_seconds']-1),1/RATE)

    def test_explicit_selection_and_missing_dependency(self):
        a=self.root/'a.wav';wav(a)
        with self.assertRaises(ValueError):convert_files([],self.root/'none')
        with self.assertRaises(ValueError):convert_files([a,a],self.root/'dupe')
        with patch('tools.audio_prepare.shutil.which',return_value=None),self.assertRaisesRegex(ValueError,'sudo apt install ffmpeg'):decoder_version()

    def test_invalid_and_empty_audio(self):
        for data in (b'',b'not audio'):
            a=self.root/'bad.opus';a.write_bytes(data)
            with self.assertRaises(ValueError):convert_files([a],self.root/'out')

    def test_cli_failure_clears_stale_assets(self):
        out=self.root/'out';out.mkdir();(out/'imported_audio.bin').write_bytes(b'old');(out/'audio.json').write_text('{}')
        bad=self.root/'bad.opus';bad.write_bytes(b'invalid')
        result=subprocess.run([sys.executable,'tools/prepare_audio.py','--file',str(bad),'--output-dir',str(out)],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('Audio preparation failed',result.stderr)
        self.assertFalse((out/'imported_audio.bin').exists())

    def test_synthetic_matching_notes_and_duration(self):
        song=normalize(Path('tests/fixtures/runtime/easy.chart').read_text())
        r=synthetic_audio(song,self.root/'one');s=synthetic_audio(song,self.root/'two')
        self.assertTrue(r['synthetic']);self.assertEqual(r,s)
        blob=(self.root/'one/imported_audio.bin').read_bytes()
        self.assertFalse(any(blob[:PRE_ROLL]));self.assertTrue(any(blob[PRE_ROLL:PRE_ROLL+1000]))
        self.assertGreater(r['source_duration_seconds'],11.333)
        self.assertLessEqual(r['output_peak'],108)

    def test_build_validation_missing_corrupt_and_silent(self):
        out=self.root/'build';out.mkdir()
        chart=Path('build/imported_chart.hpp')
        # Build helper can generate its own default fixture without existing game outputs.
        args=[sys.executable,'tools/build_audio.py','--output-dir',str(out)]
        self.assertEqual(subprocess.run(args,capture_output=True).returncode,0)
        self.assertIn('= true',(out/'imported_audio.hpp').read_text())
        self.assertEqual(subprocess.run(args+['--audio-dir','none'],capture_output=True).returncode,0)
        self.assertIn('= false',(out/'imported_audio.hpp').read_text())
        self.assertEqual(subprocess.run(args+['--private-chart'],capture_output=True).returncode,0)
        self.assertIn('= false',(out/'imported_audio.hpp').read_text())
        self.assertNotEqual(subprocess.run(args+['--audio-dir',str(self.root/'missing')],capture_output=True).returncode,0)
        song=normalize(Path('tests/fixtures/runtime/easy.chart').read_text());synthetic_audio(song,self.root/'pcm')
        (self.root/'pcm/imported_audio.bin').write_bytes(b'corrupted')
        self.assertNotEqual(subprocess.run(args+['--audio-dir',str(self.root/'pcm')],capture_output=True).returncode,0)

    def test_complete_package_selection_and_wrong_preview(self):
        package=self.root/'package';package.mkdir()
        (package/'notes.chart').write_text('[Song]\n{\nResolution = 192\n}\n[SyncTrack]\n{\n0 = B 120000\n}\n[EasySingle]\n{\n0 = N 0 1\n}\n')
        (package/'song.ini').write_text('[song]\nname = Original Test\n')
        wav(package/'song.wav',8000);wav(package/'guitar.wav',8000)
        out=self.root/'prepared'
        command=[sys.executable,'tools/prepare_song.py',str(package),'--stem','song','--stem','guitar','--output-dir',str(out)]
        result=subprocess.run(command,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        report=json.loads((out/'audio/audio.json').read_text())
        self.assertEqual(len(report['selected_package_files']),2)
        self.assertIn('prepared_chart_sha256',report)
        self.assertTrue((out/'imported_chart.hpp').exists())
        bad=command.copy();bad[4]='preview'
        self.assertNotEqual(subprocess.run(bad,capture_output=True).returncode,0)
        self.assertFalse((out/'imported_chart.hpp').exists())
        self.assertFalse((out/'audio/imported_audio.bin').exists())

    def test_complete_package_rejects_audio_ending_before_chart(self):
        package=self.root/'package';package.mkdir()
        (package/'notes.chart').write_text('[Song]\n{\nResolution = 192\n}\n[SyncTrack]\n{\n0 = B 120000\n}\n[EasySingle]\n{\n1920 = N 0 1\n}\n')
        wav(package/'song.wav',8000)
        result=subprocess.run([sys.executable,'tools/prepare_song.py',str(package),'--stem','song','--output-dir',str(self.root/'out')],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('ends before',result.stdout)

    def test_explicit_package_file_resolves_ambiguous_formats(self):
        package=self.root/'package';package.mkdir()
        (package/'notes.chart').write_text('[Song]\n{\nResolution = 192\n}\n[SyncTrack]\n{\n0 = B 120000\n}\n[EasySingle]\n{\n0 = N 0 1\n}\n')
        wav(package/'song.wav',8000)
        wav(package/'song.ogg',8000) # suffix discovery ambiguity; only selected WAV is decoded
        out=self.root/'out'
        base=[sys.executable,'tools/prepare_song.py',str(package),'--output-dir',str(out)]
        self.assertNotEqual(subprocess.run(base+['--stem','song'],capture_output=True).returncode,0)
        result=subprocess.run(base+['--audio','song.wav'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertEqual(json.loads((out/'audio/audio.json').read_text())['selected_package_files'],['song.wav'])

    def test_package_command_requires_selection(self):
        result=subprocess.run([sys.executable,'tools/prepare_song.py','tests/fixtures/midi'],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0);self.assertIn('--stem',result.stderr)


if __name__=='__main__':unittest.main()
