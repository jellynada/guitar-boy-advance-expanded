"""Public allowlist: independently regenerate exact original Arcade75 fixture.

The generic song profile remains private. Only this exact generator's verified
bytes can enter this additional public review ZIP; no owner input is accepted.
"""
import argparse
import json
from pathlib import Path
import tempfile
import zipfile
try:
    from .release_common import source_snapshot, verify_result, file_hash
    from .generate_arcade_example import prepare_example
except ImportError:
    from release_common import source_snapshot, verify_result, file_hash
    from generate_arcade_example import prepare_example


def package(root, build, output):
    root, build, output = map(Path, (root, build, output))
    files, source = source_snapshot(root); m = verify_result(build)
    if m['profile'] != 'song' or m['source_commit'] != source['source_commit'] or m['source_tree_sha256'] != source['source_tree_sha256']:
        raise ValueError('Expected matching committed generic build')
    with tempfile.TemporaryDirectory() as tmp:
        original = prepare_example(Path(tmp) / 'original')
        supplied = json.loads((build / 'prepared/song-manifest.json').read_text())
        if supplied != original: raise ValueError('Not the exact original synthetic Arcade75 generator; private publication rejected')
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, data in sorted(files.items()): z.writestr('guitar-boy-advance-expanded/' + name, data)
        z.writestr('guitar-boy-advance-expanded/SOURCE_MANIFEST.json', json.dumps(source, indent=2)+'\n')
        z.write(build / m['rom'], m['rom']); z.writestr('BUILD_MANIFEST.json', json.dumps(m, indent=2)+'\n')
        z.writestr('DERIVATION_REPORT.json', (build / 'prepared/derivation-report.json').read_bytes())
        z.writestr('READ_ME_FIRST.txt', 'ORIGINAL SYNTHETIC ARCADE75 / HANDHELD REVIEW\nNo third-party recording. No compilation needed.\nOpen '+m['rom']+' in mGBA or a compatible flash cartridge.\nSelect imported song, then Easy/Medium/Hard. START pause/resume.\nEasy LEFT/B/A; Medium LEFT/RIGHT/B/A; Hard LEFT/UP-or-DOWN/RIGHT/B/A.\nThe visible ARCADE75 / HANDHELD song title distinguishes this derivative.\nSource '+m['source_commit']+'\nROM SHA256 '+m['rom_sha256']+'\nNot hardware accepted.\n')
    with zipfile.ZipFile(output) as z:
        if z.testzip() is not None: raise ValueError('CRC failure')
        if z.read(m['rom']) != (build / m['rom']).read_bytes(): raise ValueError('Packaged ROM differs')
    print('Public original Arcade75 ZIP:',output,'SHA256',file_hash(output))
    return m


def verify_extract(root, build, archive, destination):
    files, source = source_snapshot(Path(root)); m = verify_result(Path(build))
    destination = Path(destination)
    if destination.exists(): raise ValueError('Extraction directory must be new')
    expected = {'guitar-boy-advance-expanded/'+n for n in files} | {'guitar-boy-advance-expanded/SOURCE_MANIFEST.json',
        m['rom'], 'BUILD_MANIFEST.json', 'DERIVATION_REPORT.json', 'READ_ME_FIRST.txt'}
    with zipfile.ZipFile(archive) as z:
        if len(z.namelist()) != len(expected) or set(z.namelist()) != expected or z.testzip() is not None:
            raise ValueError('Review ZIP inventory/CRC mismatch')
        for n, data in files.items():
            if z.read('guitar-boy-advance-expanded/'+n) != data: raise ValueError('ZIP source mismatch')
        if z.read(m['rom']) != (Path(build)/m['rom']).read_bytes(): raise ValueError('ZIP ROM mismatch')
        if json.loads(z.read('BUILD_MANIFEST.json')) != m or json.loads(z.read('guitar-boy-advance-expanded/SOURCE_MANIFEST.json')) != source:
            raise ValueError('ZIP manifest mismatch')
        if z.read('DERIVATION_REPORT.json') != (Path(build)/'prepared/derivation-report.json').read_bytes(): raise ValueError('ZIP provenance mismatch')
        destination.mkdir(parents=True)
        for n in sorted(expected):
            target = destination/n; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(z.read(n))
    return dict(source_commit=m['source_commit'],rom_sha256=m['rom_sha256'],archive_sha256=file_hash(archive),
                inventory='passed',crc='passed',extraction='passed',network_download_verified=False)


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--build',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--extract-to',type=Path);a=p.parse_args();package(a.repo,a.build,a.output)
    if a.extract_to: print(json.dumps(verify_extract(a.repo,a.build,a.output,a.extract_to),indent=2))
