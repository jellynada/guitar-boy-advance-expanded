"""Build only the original Mission017 composition; no owner input accepted."""
import argparse
import hashlib
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
try:
    from .release_common import source_snapshot, export_source, file_hash
    from .compose_public_demo import generate, TITLE
    from .song_pipeline import prepare, verify_prepared
except ImportError:
    from release_common import source_snapshot, export_source, file_hash
    from compose_public_demo import generate, TITLE
    from song_pipeline import prepare, verify_prepared

VERSION = 'v0.1.0-alpha-RC2'
ROM = 'Guitar-Boy-Advance-Expanded-'+VERSION+'.gba'
CANDIDATES = {'v0.1.0-alpha-RC1':'M017', VERSION:'M018'}


def verify(result):
    result=Path(result);m=json.loads((result/'manifest.json').read_text())
    if m.get('version') not in CANDIDATES:raise ValueError('Unknown demo candidate')
    ROM='Guitar-Boy-Advance-Expanded-'+m['version']+'.gba'
    if m.get('rom')!=ROM:raise ValueError('Demo candidate filename mismatch')
    if m.get('schema')!='gba-public-demo-v1' or m.get('status')!='success':raise ValueError('Not a successful public-demo build')
    for name,sha in m['file_sha256'].items():
        if name not in {ROM,ROM.replace('.gba','.elf'),'symbols.txt'} or file_hash(result/name)!=sha:raise ValueError('Demo output damaged or unreviewed')
    if set(m['file_sha256'])!={ROM,ROM.replace('.gba','.elf'),'symbols.txt'}:raise ValueError('Missing demo output')
    data=(result/ROM).read_bytes();marker=('GBA_BUILD:'+CANDIDATES[m['version']]+':public-demo:'+m['source_commit']).encode()+b'\0'
    if data.count(marker)!=1 or file_hash(result/ROM)!=m['rom_sha256']:raise ValueError('Demo ROM identity mismatch')
    if len(data)>33554432 or len(data)<192 or data[0xB2]!=0x96 or (sum(data[0xA0:0xBD])+0x19+data[0xBD])&255:raise ValueError('Invalid GBA cartridge header/budget')
    if hashlib.sha256(data[4:160]).hexdigest()!='08a0153cfd6b0ea54b938f7d209933fa849da0d56f5a34c481060c9ff2fad818':raise ValueError('Invalid GBA boot logo')
    song=verify_prepared(result/'prepared')
    if file_hash(result/'prepared/song-manifest.json')!=m['prepared_manifest_sha256']:raise ValueError('Prepared identity mismatch')
    symbols=(result/'symbols.txt').read_text()
    for forbidden in ['careless_expertsingle','soundbank_bin','mmStart','mmInit']:
        if forbidden in symbols:raise ValueError('Forbidden legacy payload/function: '+forbidden)
    for name in ['imported_audio.bin','imported_backing.bin']:
        if (result/'prepared/audio'/name).read_bytes() not in data:raise ValueError('Actual original stem missing from ROM')
    for forbidden in [b'Sunshine of Your Love',b'M014 / CREAM',b'Cream (WaveGroup)']:
        if forbidden in data:raise ValueError('Private payload marker in public ROM')
    if m['charts']!=song['runtime']['difficulties'] or song['preparation_recipe'].get('display_title')!=TITLE:raise ValueError('Demo chart/title mismatch')
    return m


def build(root, container=None):
    root=Path(root).resolve();files,source=source_snapshot(root)
    output=root/'builds/public-demo';output.mkdir(parents=True,exist_ok=True)
    stamp=source['source_commit'][:12]+'-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    job=output/stamp;job.mkdir();work=job/'guitar-boy-advance-expanded'
    try:
        export_source(files,source,work)
        composition=generate(job/'composition')
        prepare(job/'composition',job/'prepared',difficulty='All',guitar='guitar.wav',backing=['backing.wav'],max_duration=75,handheld=True,display_title=TITLE)
        shutil.copytree(job/'prepared',work/'imports/output/public-demo')
        image=(work/'scripts/toolchain-image.txt').read_text().strip()
        flags=['BUILD_PROFILE=public-demo','SOURCE_REVISION='+source['source_commit'],
               'IMPORTED_HEADER=imports/output/public-demo/imported_chart.hpp','AUDIO_DIR=imports/output/public-demo/audio']
        if container:
            actual=subprocess.check_output(['docker','inspect','--format','{{.Config.Image}}',container],text=True).strip()
            if actual!=image:raise ValueError('Existing build container is not the exact pinned toolchain image')
            command=['docker','exec','-w',str(work),container,'make','-j2',*flags]
        else:command=['bash','scripts/build-docker.sh',*flags]
        with(job/'build.log').open('w')as log:
            subprocess.run(command,cwd=work,stdout=log,stderr=subprocess.STDOUT,check=True)
        for extension in ['.gba','.elf']:shutil.copyfile(work/('guitar-boy-advance-expanded'+extension),job/ROM.replace('.gba',extension))
        image=(work/'scripts/toolchain-image.txt').read_text().strip()
        with(job/'symbols.txt').open('w')as f:
            subprocess.run((['docker','exec',container,'/opt/devkitpro/devkitARM/bin/arm-none-eabi-nm',str(job/ROM.replace('.gba','.elf'))]if container else['docker','run','--rm','-v',str(job)+':/public-demo:ro',image,'/opt/devkitpro/devkitARM/bin/arm-none-eabi-nm','/public-demo/'+ROM.replace('.gba','.elf')]),stdout=f,check=True)
        m=dict(schema='gba-public-demo-v1',status='success',version=VERSION,profile='public-demo',test_suite_revision=source['source_commit'],source_commit=source['source_commit'],source_tree_sha256=source['source_tree_sha256'],
               rom=ROM,rom_sha256=file_hash(job/ROM),rom_bytes=(job/ROM).stat().st_size,prepared_manifest_sha256=file_hash(job/'prepared/song-manifest.json'),
               composition=composition,charts=verify_prepared(job/'prepared')['runtime']['difficulties'],toolchain=image,
               legacy_commercial_assets_excluded=True,physical_hardware_verified=False,
               file_sha256={n:file_hash(job/n)for n in [ROM,ROM.replace('.gba','.elf'),'symbols.txt']})
        (job/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');(job/'SOURCE_MANIFEST.json').write_text(json.dumps(source,indent=2)+'\n')
        verify(job)
        # The source and explicit generated input are rechecked before success.
        _,current=source_snapshot(root)
        if current!=source:raise ValueError('Source changed during demo build')
        shutil.rmtree(work);(output/'LATEST.txt').write_text(stamp+'\n')
        print(json.dumps(dict(result=str(job),source_commit=m['source_commit'],rom_sha256=m['rom_sha256']),indent=2));return job
    except Exception:
        (job/'FAILED.txt').write_text('Build failed. No LATEST success was selected. Inspect build.log.\n')
        raise


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--build-container',help='Reuse an existing exact pinned-image container with the workspace mounted');a=p.parse_args();build(a.repo,a.build_container)
