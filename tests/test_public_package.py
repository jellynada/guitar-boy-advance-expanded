"""Public package boundaries, extraction and repeatable packaging regressions."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import warnings
import zipfile

from tools.adapt_chart import adapt, header
from tools.chart_importer import normalize
from tools.package_public import package
from tools.reactive_prepare import synthetic_reactive
from tools.release_common import digest, file_hash, source_snapshot, validate_assets
from tools.verify_public_package import verify_package


class PublicPackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'source'
        fixture = self.root / 'tests/fixtures/runtime/easy.chart'
        fixture.parent.mkdir(parents=True)
        fixture.write_bytes((Path(__file__).parent / 'fixtures/runtime/easy.chart').read_bytes())
        (self.root / 'README.md').write_text('synthetic fixture source\n')
        for args in [['init', '-q'], ['add', '.'], ['-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'fixture']]:
            subprocess.run(['git', '-C', str(self.root), *args], check=True)
        _, source = source_snapshot(self.root)
        self.build = self.base / 'build'
        runtime = self.build / 'runtime'
        runtime.mkdir(parents=True)
        song = normalize(fixture.read_text(), 'Synthetic Easy Test')
        (runtime / 'imported_chart.hpp').write_text(header(adapt(song, difficulty='Easy', instrument='five_fret_lead_guitar', synthetic=True)))
        synthetic_reactive(song, runtime)
        (runtime / 'imported_audio.hpp').write_text('unit fixture audio metadata\n')
        work = self.base / 'work'
        (work / 'build').mkdir(parents=True)
        (work / 'tests/fixtures/runtime').mkdir(parents=True)
        (work / 'tests/fixtures/runtime/easy.chart').write_bytes(fixture.read_bytes())
        for p in runtime.iterdir():
            (work / 'build' / p.name).write_bytes(p.read_bytes())
        assets = validate_assets(work, 'public')
        rom = 'Guitar-Boy-Advance-M014-Synthetic.gba'
        (self.build / rom).write_bytes(f'GBA_BUILD:M014:public-synthetic:{source["source_commit"]}\0'.encode() +
                                     (runtime / 'imported_audio.bin').read_bytes() + (runtime / 'imported_backing.bin').read_bytes())
        (self.build / rom.replace('.gba', '.elf')).write_bytes(b'unit fixture ELF, never emulator-tested')
        names = [rom, rom.replace('.gba', '.elf')] + ['runtime/' + name for name in ['imported_chart.hpp', 'imported_audio.hpp', 'imported_audio.bin', 'imported_backing.bin']]
        self.manifest = dict(schema='gba-build-v1', status='success', profile='public', source_commit=source['source_commit'],
                             source_tree_sha256=source['source_tree_sha256'], rom=rom, rom_bytes=(self.build / rom).stat().st_size,
                             rom_sha256=file_hash(self.build / rom), input_zip_sha256=None, assets=assets,
                             artifact_sha256={n: file_hash(self.build / n) for n in names})
        (self.build / 'manifest.json').write_text(json.dumps(self.manifest))
        (self.build / 'SOURCE_MANIFEST.json').write_text(json.dumps(source))
        self.archive = package(self.root, self.build, self.base / 'review.zip')

    def rewrite(self, change):
        with zipfile.ZipFile(self.archive) as z:
            entries = [(n, z.read(n)) for n in z.namelist()]
        with zipfile.ZipFile(self.archive, 'w') as z:
            for n, data in change(entries):
                z.writestr(n, data)

    def verify(self):
        return verify_package(self.archive, self.build, self.base / 'extracted')

    def test_intact_extraction_and_repeatable_zip(self):
        other = package(self.root, self.build, self.base / 'second.zip')
        self.assertEqual(file_hash(self.archive), file_hash(other))
        receipt = self.verify()
        self.assertEqual(receipt['rom_sha256'], self.manifest['rom_sha256'])
        self.assertFalse(receipt['network_download_verified'])

    def test_changed_rom_rejected_before_extraction(self):
        self.rewrite(lambda entries: [(n, b'bad' if n.endswith('.gba') else data) for n, data in entries])
        with self.assertRaisesRegex(ValueError, 'ROM differs'):
            self.verify()
        self.assertFalse((self.base / 'extracted').exists())

    def test_changed_source_rejected(self):
        self.rewrite(lambda entries: [(n, b'bad' if n.endswith('/README.md') else data) for n, data in entries])
        with self.assertRaisesRegex(ValueError, 'source differs'):
            self.verify()

    def test_extra_private_member_rejected(self):
        self.rewrite(lambda entries: entries + [('private/Cream.zip', b'private canary')])
        with self.assertRaisesRegex(ValueError, 'ZIP members'):
            self.verify()

    def test_path_traversal_rejected(self):
        self.rewrite(lambda entries: entries + [('../escape', b'unsafe')])
        with self.assertRaisesRegex(ValueError, 'ZIP members'):
            self.verify()
        self.assertFalse((self.base / 'escape').exists())

    def test_duplicate_member_rejected(self):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            self.rewrite(lambda entries: entries + [entries[0]])
        with self.assertRaisesRegex(ValueError, 'ZIP members'):
            self.verify()

    def test_existing_extraction_directory_rejected(self):
        (self.base / 'extracted').mkdir()
        with self.assertRaisesRegex(ValueError, 'must be new'):
            self.verify()

    def test_wrong_build_source_binding_rejected(self):
        p = self.build / 'SOURCE_MANIFEST.json'
        data = json.loads(p.read_text());data['source_commit'] = 'b' * 40;p.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'source manifest identity'):
            self.verify()


if __name__ == '__main__':
    unittest.main()
