"""Real source-export, failed-command, stale-result and public leakage guards."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import uuid

from tools.build_profile import build
from tools.release_common import (digest, export_source, file_hash, safe_source_name,
                                  source_snapshot, tree_digest, verify_result)
from tools.write_build_identity import identity


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'project with spaces'
        self.root.mkdir()
        (self.root / 'README.md').write_text('public source\n')
        (self.root / '.gitignore').write_text('/private/\n/builds/\n')
        for cmd in [['init', '-q'], ['add', '.'], ['-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'fixture']]:
            subprocess.run(['git', '-C', str(self.root), *cmd], check=True)

    def tearDown(self):
        self.temp.cleanup()

    def test_ignored_private_canary_excluded_and_not_staged(self):
        marker = uuid.uuid4().hex.encode()
        p = self.root / 'private/Cream.zip';p.parent.mkdir();p.write_bytes(marker)
        files, metadata = source_snapshot(self.root)
        self.assertNotIn(marker, b''.join(files.values()))
        self.assertNotIn('private/Cream.zip', metadata['files'])
        tracked = subprocess.check_output(['git', '-C', str(self.root), 'ls-files']).decode()
        self.assertNotIn('private', tracked)
        subprocess.run(['git', '-C', str(self.root), 'check-ignore', '-q', 'private/Cream.zip'], check=True)

    def test_tracked_private_not_protected_by_ignore(self):
        p = self.root / 'private/Cream.zip';p.parent.mkdir();p.write_bytes(b'not real music')
        subprocess.run(['git', '-C', str(self.root), 'add', '-f', 'private/Cream.zip'], check=True)
        subprocess.run(['git', '-C', str(self.root), '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'bad fixture'], check=True)
        with self.assertRaisesRegex(ValueError, 'Private/generated'):
            source_snapshot(self.root)

    def test_archive_round_trip_without_git(self):
        files, metadata = source_snapshot(self.root)
        destination = Path(self.temp.name) / 'archive'
        export_source(files, metadata, destination)
        self.assertEqual(source_snapshot(destination), (files, metadata))

    def test_changed_archive_source_rejected(self):
        files, metadata = source_snapshot(self.root)
        destination = Path(self.temp.name) / 'archive'
        export_source(files, metadata, destination)
        (destination / 'README.md').write_text('changed')
        with self.assertRaisesRegex(ValueError, 'changed or is incomplete'):
            source_snapshot(destination)

    def test_archive_missing_source_rejected(self):
        files, metadata = source_snapshot(self.root)
        destination = Path(self.temp.name) / 'archive'
        export_source(files, metadata, destination)
        (destination / 'README.md').unlink()
        with self.assertRaises(ValueError):source_snapshot(destination)

    def test_dirty_source_rejected(self):
        (self.root / 'README.md').write_text('uncommitted')
        with self.assertRaisesRegex(ValueError, 'uncommitted'):
            source_snapshot(self.root)

    def test_missing_revision_rejected(self):
        p = Path(self.temp.name) / 'notgit';p.mkdir()
        with self.assertRaisesRegex(ValueError, 'No Git revision'):
            source_snapshot(p)

    def test_forbidden_paths_and_payloads(self):
        for name in ['private/x', 'builds/private/x.gba', 'downloads/anything', 'imports/output/song/audio.json',
                     'source/Cream.zip', 'source/recording.opus', 'source/generated.bin', 'include/imported_chart.hpp',
                     '../README.md', '/README.md', 'source\\bad', 'unknown/x.txt']:
            with self.subTest(name=name), self.assertRaises(ValueError):safe_source_name(name)

    def test_only_reviewed_workflow_is_exportable(self):
        self.assertEqual(safe_source_name('.github/workflows/foundation.yml'), '.github/workflows/foundation.yml')
        for name in ['.github/workflows/unreviewed.yml', '.github/secrets.txt',
                     '.github/workflows/Cream.zip', '.github/workflows/private/key.txt']:
            with self.subTest(name=name), self.assertRaises(ValueError):
                safe_source_name(name)

    def test_source_symlink_rejected(self):
        (self.root / 'docs').mkdir();(self.root / 'docs/link').symlink_to('../README.md')
        subprocess.run(['git', '-C', str(self.root), 'add', 'docs'], check=True)
        subprocess.run(['git', '-C', str(self.root), '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'symlink fixture'], check=True)
        with self.assertRaisesRegex(ValueError, 'symlinks'):source_snapshot(self.root)

    def test_missing_private_input_invalidates_old_success(self):
        out = self.root / 'builds/private';out.mkdir(parents=True)
        (out / 'LATEST.txt').write_text('old\n');(out / 'old.gba').write_bytes(b'old')
        with self.assertRaisesRegex(ValueError, 'Missing private/Cream.zip'):
            build(self.root, 'cream')
        self.assertFalse((out / 'LATEST.txt').exists())
        self.assertEqual((out / 'old.gba').read_bytes(), b'old')
        self.assertEqual(json.loads((out / 'LAST_ATTEMPT.json').read_text())['status'], 'failed')

    def test_actual_failed_command_never_selects_old_rom(self):
        out = self.root / 'builds/public';out.mkdir(parents=True)
        (out / 'LATEST.txt').write_text('old');(out / 'old.gba').write_bytes(b'old')
        binpath = Path(self.temp.name) / 'bin';binpath.mkdir()
        docker = binpath / 'docker';docker.write_text('#!/bin/sh\necho deliberate Docker failure\nexit 37\n');docker.chmod(0o755)
        with patch.dict(os.environ, {'PATH': str(binpath) + os.pathsep + os.environ['PATH']}):
            with self.assertRaisesRegex(ValueError, 'exit37'):
                build(self.root, 'public')
        self.assertFalse((out / 'LATEST.txt').exists())
        self.assertEqual((out / 'old.gba').read_bytes(), b'old')
        self.assertEqual(json.loads((out / 'LAST_ATTEMPT.json').read_text())['status'], 'failed')

    def test_public_profile_rejects_private_argument(self):
        with self.assertRaisesRegex(ValueError, 'do not accept private inputs'):
            build(self.root, 'public', self.root / 'Cream.zip')

    def artifact(self, profile='public'):
        folder = Path(self.temp.name) / 'artifact';folder.mkdir()
        filename = 'Guitar-Boy-Advance-M014-Synthetic.gba' if profile == 'public' else 'Guitar-Boy-Advance-M014-Cream-Private.gba'
        label = 'public-synthetic' if profile == 'public' else 'cream-private'
        (folder / 'runtime').mkdir()
        for name, data in [('imported_chart.hpp', b'fixture chart'), ('imported_audio.hpp', b'fixture metadata'),
                           ('imported_audio.bin', b'fixture guitar'), ('imported_backing.bin', b'fixture backing')]:
            (folder / 'runtime' / name).write_bytes(data)
        rom = f'GBA_BUILD:M014:{label}:'.encode() + b'a' * 40 + b'\0fixture guitarfixture backing'
        (folder / filename).write_bytes(rom);(folder / filename.replace('.gba', '.elf')).write_bytes(b'unit fixture elf')
        names = [filename, filename.replace('.gba', '.elf')] + ['runtime/' + p.name for p in (folder / 'runtime').iterdir()]
        m = {'schema': 'gba-build-v1', 'status': 'success', 'profile': profile, 'source_commit': 'a' * 40,
             'rom': filename, 'rom_bytes': len(rom), 'rom_sha256': digest(rom),
             'artifact_sha256': {n: file_hash(folder / n) for n in names}, 'input_zip_sha256': None,
             'assets': {'note_heads': 25, 'genuine_sustains': 6, 'chart_sha256': file_hash(folder / 'runtime/imported_chart.hpp'),
                        'guitar_sha256': file_hash(folder / 'runtime/imported_audio.bin'), 'backing_sha256': file_hash(folder / 'runtime/imported_backing.bin')}}
        (folder / 'manifest.json').write_text(json.dumps(m));return folder, m

    def test_intact_artifact_inventory_accepted(self):
        folder, m = self.artifact();self.assertEqual(verify_result(folder, True), m)

    def test_private_result_cannot_be_public(self):
        folder, _ = self.artifact('cream')
        with self.assertRaisesRegex(ValueError, 'private build cannot'):
            verify_result(folder, True)

    def test_stale_rom_rejected(self):
        folder, m = self.artifact();(folder / m['rom']).write_bytes(b'old ROM')
        with self.assertRaisesRegex(ValueError, 'Stale or damaged'):verify_result(folder, True)

    def test_stale_runtime_rejected(self):
        folder, _ = self.artifact();(folder / 'runtime/imported_audio.bin').write_bytes(b'wrong')
        with self.assertRaisesRegex(ValueError, 'Stale or damaged'):verify_result(folder, True)

    def test_missing_elf_inventory_rejected(self):
        folder, m = self.artifact();del m['artifact_sha256'][m['rom'].replace('.gba', '.elf')]
        (folder / 'manifest.json').write_text(json.dumps(m))
        with self.assertRaisesRegex(ValueError, 'Incomplete'):verify_result(folder, True)

    def test_wrong_revision_marker_rejected_even_with_updated_hash(self):
        folder, m = self.artifact();m['source_commit'] = 'b' * 40
        (folder / 'manifest.json').write_text(json.dumps(m))
        with self.assertRaisesRegex(ValueError, 'identity/hash'):verify_result(folder, True)

    def test_identity_rejects_shell_or_macro_injection(self):
        for revision in ['bad', 'a' * 40 + '"', '$(anything)']:
            with self.assertRaises(ValueError):identity('public-synthetic', revision)


if __name__ == '__main__':unittest.main()
