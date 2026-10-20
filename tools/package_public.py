#!/usr/bin/env python3
"""Package only committed audited source plus a verified synthetic-profile ROM."""
import argparse
import json
from pathlib import Path
import tempfile
import zipfile

try:
    from .release_common import export_source, file_hash, source_snapshot, validate_assets, verify_result
except ImportError:
    from release_common import export_source, file_hash, source_snapshot, validate_assets, verify_result


def package(root, result, output):
    root, result, output = Path(root), Path(result), Path(output)
    files, source = source_snapshot(root)
    manifest = verify_result(result, public_only=True)
    if (manifest['source_commit'], manifest['source_tree_sha256']) != (source['source_commit'], source['source_tree_sha256']):
        raise ValueError('Build and source revision differ; rebuild the public profile first')
    # Do not trust a public label alone: regenerate the known fixture and compare.
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / 'engine'
        export_source(files, source, work)
        (work / 'build').mkdir()
        for name in ['imported_chart.hpp', 'imported_audio.hpp', 'imported_audio.bin', 'imported_backing.bin']:
            (work / 'build' / name).write_bytes((result / 'runtime' / name).read_bytes())
        if validate_assets(work, 'public') != manifest['assets']:
            raise ValueError('Build does not contain the exact public fixture')
    output.parent.mkdir(parents=True, exist_ok=True)
    # Publish atomically; on failure do not leave a partial ZIP as a successful package.
    with tempfile.NamedTemporaryFile(dir=output.parent, suffix='.zip', delete=False) as temp:
        temporary = Path(temp.name)
    try:
        with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for name, data in sorted(files.items()):
                z.writestr('guitar-boy-advance-expanded/' + name, data)
            z.writestr('guitar-boy-advance-expanded/SOURCE_MANIFEST.json', json.dumps(source, indent=2) + '\n')
            z.write(result / manifest['rom'], manifest['rom'])
            z.writestr('BUILD_MANIFEST.json', json.dumps(manifest, indent=2) + '\n')
            z.writestr('READ_ME_FIRST.txt',
                        'MISSION013 SYNTHETIC REVIEW BUILD\nExtract All. Install mGBA from https://mgba.io/downloads.html.\n'
                        'File > Load ROM > ' + manifest['rom'] + '\n'
                        'This public test song is synthetic. No Cream recording/chart is included.\n'
                        'To build privately: open guitar-boy-advance-expanded/docs/WINDOWS_PRIVATE_BUILD.md.\n'
                        'Place your own ZIP in private/Cream.zip and double-click Build-Cream-ROM.bat.\n'
                        'Review candidate, not a stable release. Read docs/KNOWN_ISSUES.md.\n')
        with zipfile.ZipFile(temporary) as z:
            if z.testzip() is not None:
                raise ValueError('Public ZIP CRC failed')
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    print('PUBLIC PACKAGE: ' + str(output.resolve()) + '\nSHA-256: ' + file_hash(output))
    return output


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--build', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    try:
        package(a.repo, a.build, a.output)
    except (ValueError, OSError, KeyError) as error:
        raise SystemExit('PUBLIC PACKAGE REJECTED: ' + str(error))
