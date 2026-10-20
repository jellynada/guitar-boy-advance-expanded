#!/usr/bin/env python3
"""Verify a public ZIP against its successful build before extracting it."""
import argparse
import json
from pathlib import Path
import stat
import zipfile

try:
    from .release_common import digest, file_hash, safe_source_name, source_snapshot, verify_result
except ImportError:
    from release_common import digest, file_hash, safe_source_name, source_snapshot, verify_result

PREFIX = 'guitar-boy-advance-expanded/'


def verify_package(archive, build, destination):
    archive, build, destination = Path(archive), Path(build), Path(destination)
    manifest = verify_result(build, public_only=True)
    source = json.loads((build / 'SOURCE_MANIFEST.json').read_text())
    if (source['source_commit'], source['source_tree_sha256']) != (manifest['source_commit'], manifest['source_tree_sha256']):
        raise ValueError('Build source manifest identity mismatch')
    if destination.exists():
        raise ValueError('Extraction destination must be new')
    with zipfile.ZipFile(archive) as z:
        entries = z.infolist()
        names = [e.filename for e in entries]
        expected = {PREFIX + n for n in source['files']} | {
            PREFIX + 'SOURCE_MANIFEST.json', manifest['rom'], 'BUILD_MANIFEST.json', 'READ_ME_FIRST.txt'}
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError('Unexpected, duplicate or missing ZIP members')
        if len(entries) > 10000 or sum(e.file_size for e in entries) > 128 * 1024**2:
            raise ValueError('ZIP exceeds review package limits')
        for e in entries:
            if e.flag_bits & 1 or e.is_dir() or stat.S_ISLNK(e.external_attr >> 16) or e.file_size > 32 * 1024**2:
                raise ValueError('Unsafe ZIP member: ' + e.filename)
            if e.filename.startswith(PREFIX) and e.filename != PREFIX + 'SOURCE_MANIFEST.json':
                safe_source_name(e.filename[len(PREFIX):])
        if z.testzip() is not None:
            raise ValueError('ZIP CRC failure')
        if json.loads(z.read('BUILD_MANIFEST.json')) != manifest or json.loads(z.read(PREFIX + 'SOURCE_MANIFEST.json')) != source:
            raise ValueError('ZIP manifest differs from successful build')
        if digest(z.read(manifest['rom'])) != manifest['rom_sha256'] or len(z.read(manifest['rom'])) != manifest['rom_bytes']:
            raise ValueError('ZIP ROM differs from successful build')
        for name, expected_hash in source['files'].items():
            if digest(z.read(PREFIX + name)) != expected_hash:
                raise ValueError('ZIP source differs: ' + name)
        # Extract only after complete inventory, path, content and CRC validation.
        destination.mkdir(parents=True)
        for e in entries:
            path = destination / e.filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(z.read(e))
    _, extracted_source = source_snapshot(destination / PREFIX)
    if extracted_source != source:
        raise ValueError('Extracted source manifest mismatch')
    receipt = dict(schema='gba-public-package-verification-v1', source_commit=manifest['source_commit'],
                   archive=archive.name, archive_sha256=file_hash(archive), rom=manifest['rom'],
                   rom_sha256=manifest['rom_sha256'], rom_bytes=manifest['rom_bytes'],
                   zip_crc='passed', source_inventory='passed', extraction='passed',
                   network_download_verified=False)
    return receipt


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('archive', type=Path)
    p.add_argument('--build', type=Path, required=True)
    p.add_argument('--extract-to', type=Path, required=True)
    p.add_argument('--receipt', type=Path, required=True)
    a = p.parse_args()
    try:
        result = verify_package(a.archive, a.build, a.extract_to)
        a.receipt.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(result, indent=2))
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        raise SystemExit('PUBLIC PACKAGE REJECTED: ' + str(error))
