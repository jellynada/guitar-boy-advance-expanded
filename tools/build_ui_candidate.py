"""Build a new M021 public-safe or owner-local candidate from clean committed source.
Never uploads. The frozen RC2 builder and files remain independent.
"""
import argparse,json,hashlib,shutil,subprocess,os
from pathlib import Path
from datetime import datetime,timezone
try:
 from .release_common import source_snapshot,export_source,file_hash
 from .song_pipeline import prepare,verify_prepared
 from .compose_public_demo import generate
except ImportError:
 from release_common import source_snapshot,export_source,file_hash
 from song_pipeline import prepare,verify_prepared
 from compose_public_demo import generate

def verify(folder):
 folder=Path(folder);m=json.loads((folder/'manifest.json').read_text())
 if m['schema']!='gba-ui-candidate-v1' or m['status']!='success':raise ValueError('Not an M021 candidate')
 if set(m['file_sha256'])!={m['rom'],m['elf'],'symbols.txt'}:raise ValueError('Incomplete artifact inventory')
 if (m['profile'],m['build_profile'])not in [('public','public-demo'),('private','song-private')]:raise ValueError('Invalid candidate profile')
 for name,h in m['file_sha256'].items():
  if '/' in name or '\\'in name or name not in {m['rom'],m['elf'],'symbols.txt'}or file_hash(folder/name)!=h:raise ValueError('Candidate artifact changed')
 data=(folder/m['rom']).read_bytes();profile=m['build_profile'];prefix='M018'if profile=='public-demo'else'M014'
 marker=f"GBA_BUILD:{prefix}:{profile}:{m['source_commit']}".encode()+b'\0'
 if data.count(marker)!=1:raise ValueError('Foreign/stale source identity')
 if file_hash(folder/m['rom'])!=m['rom_sha256']or len(data)!=m['rom_bytes']:raise ValueError('ROM identity mismatch')
 if len(data)>33554432 or data[0xB2]!=0x96 or (sum(data[0xA0:0xBD])+0x19+data[0xBD])&255:raise ValueError('Invalid cartridge header')
 p=verify_prepared(folder/'prepared')
 if file_hash(folder/'prepared/song-manifest.json')!=m['prepared_manifest_sha256']:raise ValueError('Prepared source mismatch')
 for name in ['imported_audio.bin','imported_backing.bin']:
  if (folder/'prepared/audio'/name).read_bytes()not in data:raise ValueError('Prepared stem not embedded')
 if m['profile']=='public':
  symbols=(folder/'symbols.txt').read_text()
  if any(x in symbols for x in ['soundbank_bin','careless_expertsingle','mmStart','mmInit']):raise ValueError('Legacy content leaked')
  if any(x in data for x in [b'Sunshine of Your Love',b'Cream (WaveGroup)',b'M014 / CREAM']):raise ValueError('Private content leaked')
  if b'Synth Demo\0'not in data or p['preparation_recipe'].get('display_title')!='Copper Circuit':raise ValueError('Wrong public composition/display alias')
 return m

def build(root,profile='public',prepared=None):
 root=Path(root).resolve();files,source=source_snapshot(root)
 if profile=='public'and prepared is not None:raise ValueError('Public build never accepts private inputs')
 if profile=='private'and prepared is None:raise ValueError('Private build needs an explicitly verified prepared directory')
 job=root/'builds/m021-candidates'/profile/(source['source_commit'][:12]+'-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'));job.mkdir(parents=True)
 if profile=='public':
  generate(job/'composition');prepare(job/'composition',job/'prepared',difficulty='All',guitar='guitar.wav',backing=['backing.wav'],max_duration=75,handheld=True,display_title='Copper Circuit')
 else:verify_prepared(prepared);shutil.copytree(prepared,job/'prepared')
 work=job/'engine';export_source(files,source,work);shutil.copytree(job/'prepared',work/'imports/output/ui-song')
 build_profile='public-demo'if profile=='public'else'song-private';target='Guitar-Boy-Advance-M021-'+profile.title()
 flags=['BUILD_PROFILE='+build_profile,'SOURCE_REVISION='+source['source_commit'],'IMPORTED_HEADER=imports/output/ui-song/imported_chart.hpp','AUDIO_DIR=imports/output/ui-song/audio','TARGET='+target]
 if profile=='private':flags+=['SONG_METADATA=imports/output/ui-song/normalized-song.json']
 with(job/'build.log').open('w')as log:subprocess.run(['bash','scripts/build-docker.sh',*flags],cwd=work,stdout=log,stderr=subprocess.STDOUT,check=True)
 for ext in ['.gba','.elf']:shutil.copy2(work/(target+ext),job/(target+ext))
 image=(work/'scripts/toolchain-image.txt').read_text().strip()
 with(job/'symbols.txt').open('w')as f:subprocess.run(['docker','run','--rm','-v',str(job)+':/candidate:ro',image,'/opt/devkitpro/devkitARM/bin/arm-none-eabi-nm','/candidate/'+target+'.elf'],stdout=f,check=True)
 names=[target+'.gba',target+'.elf','symbols.txt'];m=dict(schema='gba-ui-candidate-v1',status='success',profile=profile,build_profile=build_profile,source_commit=source['source_commit'],source_tree_sha256=source['source_tree_sha256'],rom=names[0],elf=names[1],rom_sha256=file_hash(job/names[0]),rom_bytes=(job/names[0]).stat().st_size,prepared_manifest_sha256=file_hash(job/'prepared/song-manifest.json'),file_sha256={n:file_hash(job/n)for n in names},toolchain=image,hardware_verified=False,release_promotion='blocked; strict ordinary output is a separate gate')
 (job/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');verify(job)
 _,current=source_snapshot(root)
 if current!=source:raise ValueError('Source changed during build')
 (root/'builds/m021-candidates'/profile/'LATEST.txt').write_text(str(job.relative_to(root))+'\n')
 print(json.dumps(dict(build=str(job),source_commit=m['source_commit'],rom_sha256=m['rom_sha256']),indent=2));return job
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--profile',choices=['public','private'],default='public');p.add_argument('--prepared',type=Path);a=p.parse_args();build(a.repo,a.profile,a.prepared)
