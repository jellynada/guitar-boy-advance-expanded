"""Original multi-song contracts, malformed inputs and public isolation."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import zipfile

from tools.generate_song_examples import generate
from tools.build_profile import build
from tools.release_common import file_hash, safe_source_name, verify_result
from tools.song_pipeline import prepare, verify_prepared, MANIFEST


class SongPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = tempfile.TemporaryDirectory()
        root = Path(cls.data.name)
        cls.pulse, cls.drift = generate(root / 'examples')
        cls.prepared = root / 'prepared'
        prepare(cls.drift, cls.prepared, guitar='lead.wav', backing=['accompaniment.wav'])

    @classmethod
    def tearDownClass(cls):
        cls.data.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ready = self.root / 'prepared'
        shutil.copytree(self.prepared, self.ready)

    def test_two_distinct_packages_and_modes(self):
        pulse = self.root / 'pulse'
        m = prepare(self.pulse, pulse, mix=['melody.wav'])
        other = verify_prepared(self.ready)
        self.assertEqual(m['runtime']['note_heads'], 6)
        self.assertEqual(other['runtime']['note_heads'], 8)
        self.assertEqual(m['runtime']['genuine_sustains'], 2)
        self.assertEqual(other['runtime']['genuine_sustains'], 3)
        self.assertEqual(m['source']['format'], 'chart')
        self.assertEqual(other['source']['format'], 'midi')
        self.assertEqual(m['runtime']['physical_controls'], ['LEFT', 'B', 'A'])
        self.assertNotEqual(m['audio']['source_samples'], other['audio']['source_samples'])
        self.assertNotEqual(m['file_sha256']['imported_chart.hpp'], other['file_sha256']['imported_chart.hpp'])
        self.assertEqual((pulse / 'audio/imported_backing.bin').read_bytes(), bytes(16))

    def test_repeat_preparation_identical(self):
        again = self.root / 'again'
        prepare(self.drift, again, guitar='lead.wav', backing=['accompaniment.wav'])
        self.assertEqual((self.ready / MANIFEST).read_bytes(), (again / MANIFEST).read_bytes())
        for path in self.ready.rglob('*'):
            if path.is_file():
                self.assertEqual(path.read_bytes(), (again / path.relative_to(self.ready)).read_bytes())

    def test_midi_tempo_and_ini_offset_preserved(self):
        data = json.loads((self.ready / 'normalized-song.json').read_text())
        notes = json.loads((self.ready / 'adapted.json').read_text())['notes']
        self.assertEqual(len(data['tempo_map']), 3)
        self.assertEqual(notes[0]['start_us'], 125000)
        self.assertEqual(notes[3]['start_us'], 1875000)
        self.assertEqual(notes[0]['runtime_tick'], round(2.125 * 16777216))
        self.assertEqual(notes[1]['button'], 'B')

    def test_supported_compressed_audio_formats(self):
        for extension, codec in [('ogg', 'libvorbis'), ('mp3', 'libmp3lame'), ('opus', 'libopus')]:
            with self.subTest(extension=extension):
                source = self.root / extension;shutil.copytree(self.pulse, source)
                target = source / ('song.' + extension)
                subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(source / 'melody.wav'),
                                '-c:a', codec, str(target)], check=True)
                out = self.root / ('prepared-' + extension)
                prepare(source, out, mix=[target.name])
                self.assertEqual(verify_prepared(out)['audio']['mode'], 'fixed')

    def test_unknown_schema_rejected(self):
        p = self.ready / MANIFEST;m = json.loads(p.read_text());m['schema_version'] = 'future-v99';p.write_text(json.dumps(m))
        with self.assertRaisesRegex(ValueError, 'Unsupported'):
            verify_prepared(self.ready)

    def test_tampered_audio_rejected(self):
        (self.ready / 'audio/imported_audio.bin').write_bytes(b'bad')
        with self.assertRaisesRegex(ValueError, 'changed or is damaged'):
            verify_prepared(self.ready)

    def test_tampered_header_with_new_hash_still_rejected(self):
        p = self.ready / 'imported_chart.hpp';p.write_text(p.read_text().replace('8;', '7;', 1))
        manifest = self.ready / MANIFEST;m = json.loads(manifest.read_text());m['file_sha256']['imported_chart.hpp'] = file_hash(p);manifest.write_text(json.dumps(m))
        with self.assertRaisesRegex(ValueError, 'runtime differs'):
            verify_prepared(self.ready)

    def test_tampered_count_rejected(self):
        p = self.ready / MANIFEST;m = json.loads(p.read_text());m['runtime']['note_heads'] = 395;p.write_text(json.dumps(m))
        with self.assertRaisesRegex(ValueError, 'metadata mismatch'):
            verify_prepared(self.ready)

    def test_tampered_source_metadata_rejected(self):
        p = self.ready / MANIFEST;m = json.loads(p.read_text());m['normalized']['timing']['effective_offset_seconds'] = '0';p.write_text(json.dumps(m))
        with self.assertRaisesRegex(ValueError, 'source/selection metadata'):
            verify_prepared(self.ready)

    def test_prepared_pcm_budget_checked_before_read(self):
        with (self.ready / 'audio/imported_audio.bin').open('wb') as f:
            f.truncate(33 * 1024**2)
        with self.assertRaisesRegex(ValueError, 'limits'):
            verify_prepared(self.ready)

    def test_missing_file_rejected(self):
        (self.ready / 'adapted.json').unlink()
        with self.assertRaisesRegex(ValueError, 'missing or unexpected'):
            verify_prepared(self.ready)

    def test_extra_file_rejected(self):
        (self.ready / 'Cream.zip').write_bytes(b'canary')
        with self.assertRaisesRegex(ValueError, 'missing or unexpected'):
            verify_prepared(self.ready)

    def test_symlink_rejected(self):
        p = self.ready / 'adapted.json';p.unlink();p.symlink_to(self.prepared / 'adapted.json')
        with self.assertRaisesRegex(ValueError, 'symlinks'):
            verify_prepared(self.ready)

    def test_existing_output_is_preserved(self):
        original = file_hash(self.ready / MANIFEST)
        with self.assertRaisesRegex(ValueError, 'new directory'):
            prepare(self.pulse, self.ready, mix=['melody.wav'])
        self.assertEqual(file_hash(self.ready / MANIFEST), original)

    def test_explicit_distinct_selection_required(self):
        for kwargs in [{}, {'mix': ['melody.wav', 'melody.wav']},
                       {'guitar': 'melody.wav'}, {'mix': ['melody.wav'], 'guitar': 'melody.wav'}]:
            with self.subTest(kwargs=kwargs):
                output = self.root / ('invalid-' + str(len(list(self.root.iterdir()))))
                with self.assertRaisesRegex(ValueError, 'Choose'):
                    prepare(self.pulse, output, **kwargs)
                self.assertFalse((output / MANIFEST).exists())
                self.assertEqual(json.loads((output / 'validation-report.json').read_text())['status'], 'invalid')

    def test_unsupported_lane_rejected_without_dropping_notes(self):
        source = self.root / 'song';shutil.copytree(self.pulse, source)
        p = source / 'notes.chart';p.write_text(p.read_text().replace('0 = N 0 1', '0 = N 4 1'))
        with self.assertRaises(ValueError):
            prepare(source, self.root / 'out', mix=['melody.wav'])
        self.assertFalse((self.root / 'out' / MANIFEST).exists())

    def test_sustain_beyond_audio_rejected(self):
        source = self.root / 'song';shutil.copytree(self.pulse, source)
        p = source / 'notes.chart';p.write_text(p.read_text().replace('0 = N 0 1', '0 = N 0 3840'))
        with self.assertRaisesRegex(ValueError, 'sustain end'):
            prepare(source, self.root / 'out', mix=['melody.wav'])

    def test_unsafe_zip_rejected(self):
        source = self.root / 'bad.zip'
        with zipfile.ZipFile(source, 'w') as z:
            z.writestr('../escape.chart', b'bad')
        with self.assertRaisesRegex(ValueError, 'Unsafe ZIP path'):
            prepare(source, self.root / 'out', mix=['melody.wav'])
        self.assertFalse((self.root / 'escape.chart').exists())

    def test_song_failure_preserves_cream_build_selection(self):
        private = self.root / 'builds/private';private.mkdir(parents=True)
        (private / 'LATEST.txt').write_text('existing-Cream-build\n')
        with self.assertRaisesRegex(ValueError, 'requires --input'):
            build(self.root, 'song')
        self.assertEqual((private / 'LATEST.txt').read_text(), 'existing-Cream-build\n')
        self.assertFalse((private / 'songs/LATEST.txt').exists())

    def test_corrupt_preparation_invalidates_generic_success_pointer(self):
        out = self.root / 'builds/private/songs';out.mkdir(parents=True)
        (out / 'LATEST.txt').write_text('old');(out / 'old.gba').write_bytes(b'old')
        (self.ready / 'imported_chart.hpp').write_text('damaged')
        with self.assertRaisesRegex(ValueError, 'changed or is damaged'):
            build(self.root, 'song', self.ready)
        self.assertFalse((out / 'LATEST.txt').exists())
        self.assertEqual((out / 'old.gba').read_bytes(), b'old')

    def test_generic_profile_cannot_enter_public_packager(self):
        (self.root / 'manifest.json').write_text(json.dumps(dict(schema='gba-build-v1', status='success', profile='song')))
        with self.assertRaisesRegex(ValueError, 'private build cannot'):
            verify_result(self.root, public_only=True)
        for name in ['tools/song-manifest.json', 'tests/normalized-song.json']:
            with self.assertRaises(ValueError):
                safe_source_name(name)

    def test_build_pcm_validation_error_is_actionable(self):
        p = self.ready / 'audio/audio.json';m = json.loads(p.read_text());m['channels'] = 2;p.write_text(json.dumps(m))
        manifest = self.ready / MANIFEST;m = json.loads(manifest.read_text());m['file_sha256']['audio/audio.json'] = file_hash(p);manifest.write_text(json.dumps(m))
        with self.assertRaisesRegex(ValueError, 'audio format'):
            verify_prepared(self.ready)


if __name__ == '__main__':
    unittest.main()
