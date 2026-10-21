"""Player-only public ZIP, authorized by exact original-content regeneration."""
import argparse
import json
from pathlib import Path
import tempfile
import zipfile
try:
    from .build_public_demo import verify, ROM
    from .compose_public_demo import generate, TITLE
    from .song_pipeline import prepare
    from .release_common import source_snapshot, file_hash
except ImportError:
    from build_public_demo import verify, ROM
    from compose_public_demo import generate, TITLE
    from song_pipeline import prepare
    from release_common import source_snapshot, file_hash

ZIP = ROM.replace('.gba','.zip')


def package(root, result, destination):
    root,result,destination=map(Path,(root,result,destination));m=verify(result);files,source=source_snapshot(root)
    if m['source_commit']!=source['source_commit'] or m['source_tree_sha256']!=source['source_tree_sha256']:raise ValueError('Build/source mismatch')
    # Ignore all owner folders, historical exports and existing downloaded ZIPs.
    with tempfile.TemporaryDirectory()as t:
        t=Path(t);composition=generate(t/'source')
        expected=prepare(t/'source',t/'prepared',difficulty='All',guitar='guitar.wav',backing=['backing.wav'],max_duration=75,handheld=True,display_title=TITLE)
        if composition!=m['composition'] or expected!=json.loads((result/'prepared/song-manifest.json').read_text()):raise ValueError('Not the exact original public composition')
    payload={ROM:(result/ROM).read_bytes(),'BUILD_MANIFEST.json':(result/'manifest.json').read_bytes(),
             'SHA256SUMS.txt':(m['rom_sha256']+'  '+ROM+'\n').encode(),
             'README.txt':('GUITAR BOY ADVANCE EXPANDED - v0.1.0-alpha-RC1\n\nOpen '+ROM+' in mGBA, or copy it to a compatible GBA flash cartridge.\nNo compilation is needed.\n\nChoose Copper Circuit, then Easy/Medium/Hard.\nEasy: LEFT / B / A\nMedium: LEFT / RIGHT / B / A\nHard: LEFT / UP-or-DOWN / RIGHT / B / A\nEvery note needs a fresh press. Keep sustains held for bonuses.\nMisses mute guitar; a valid hit brings it back.\nSTART: pause/resume. SELECT while paused: return.\nResults: A/START replay; B/SELECT song selection.\n\nOriginal 75-second composition, plus a 2-second count-in.\nSource: '+m['source_commit']+'\nROM SHA256: '+m['rom_sha256']+'\n\nReal-GBA owner acceptance pending. Public-demo strict emulator output\ncomparisons currently fail the unchanged 1ms limit: release gate blocked.\nHistorical full-length Cream emulator\noutput findings remain unresolved; this ROM contains no Cream recording.\nInput diagnostics use the historical Easy test; Hard alias is described above.\nRead LICENSES/OWNER_PERMISSION.txt and included third-party notices.\n').encode()}
    for name in sorted(files):
        if name.startswith('docs/licenses/') or name=='docs/DEMO_CONTENT_PROVENANCE.md':payload['LICENSES/'+Path(name).name]=files[name]
        if name in {'docs/KNOWN_ISSUES.md','docs/OWNER_M017_PLAYTEST.md'}:payload[Path(name).name]=files[name]
    if 'LICENSES/OWNER_PERMISSION.txt' not in payload or 'LICENSES/TONC-MIT.txt' not in payload:raise ValueError('Missing publication authority/notices')
    destination.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(destination,'x',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for name,data in sorted(payload.items()):
            entry=zipfile.ZipInfo(name,(1980,1,1,0,0,0));entry.compress_type=zipfile.ZIP_DEFLATED;z.writestr(entry,data)
    with zipfile.ZipFile(destination)as z:
        if z.testzip() is not None or set(z.namelist())!=set(payload):raise ValueError('ZIP CRC/inventory failed')
        for name,data in payload.items():
            if z.read(name)!=data:raise ValueError('ZIP content mismatch')
    receipt=dict(source_commit=m['source_commit'],archive_sha256=file_hash(destination),rom_sha256=m['rom_sha256'],
                 original_content_regenerated=True,legacy_commercial_payloads_excluded=True,crc='passed',payload_sha256={n:__import__('hashlib').sha256(b).hexdigest()for n,b in payload.items()},network_download_verified=False)
    destination.with_suffix('.verification.json').write_text(json.dumps(receipt,indent=2)+'\n');return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--build',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(package(a.repo,a.build,a.output),indent=2))
