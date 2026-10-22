"""Build an immutable committed-source multi-song candidate; never uploads.
On Windows, run with --native using the existing process-local devkitARM/make
environment. Otherwise use the pinned existing Docker toolchain.
"""
import argparse,datetime,json,os,shutil,subprocess,re
from pathlib import Path
try:
 from .release_common import source_snapshot,export_source,file_hash
 from .song_collection import generate_collection,verify_rom
except ImportError:
 from release_common import source_snapshot,export_source,file_hash
 from song_collection import generate_collection,verify_rom
def build(root,spec,native=False):
 root=Path(root).absolute();files,source=source_snapshot(root)
 profile=spec['profile'];revision=source['source_commit']
 job=root/'builds/m022-candidates'/profile/(revision[:12]+'-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'));job.mkdir(parents=True)
 generate_collection(spec,job/'assets')
 work=job/'engine';export_source(files,source,work)
 target='Guitar-Boy-Advance-M022-'+profile.title()
 flags=['BUILD_PROFILE=collection-'+profile,'SOURCE_REVISION='+revision,'COLLECTION_DIR='+str(job/'assets').replace('\\','/'),'TARGET='+target]
 with(job/'build.log').open('w')as log:
  if native:
   subprocess.run(['make','-j2','PYTHON='+str(Path(os.sys.executable)).replace('\\','/'),*flags,'build'],cwd=work,stdout=log,stderr=subprocess.STDOUT,check=True)
  else:
   # The volume contains only the audited source and explicitly selected packages.
   shutil.copytree(job/'assets',work/'collection-input')
   flags=[f for f in flags if not f.startswith('COLLECTION_DIR=')]+['COLLECTION_DIR=/workspace/guitar-boy-advance-expanded/collection-input']
   result=subprocess.run(['bash','scripts/build-docker.sh',*flags],cwd=work,stdout=log,stderr=subprocess.STDOUT)
   if result.returncode:
    log.flush();print((job/'build.log').read_text()[-20000:]);raise subprocess.CalledProcessError(result.returncode,result.args)
 for ext in ['.gba','.elf']:shutil.copy2(work/(target+ext),job/(target+ext))
 if native:
  prefix=str(Path(os.environ['DEVKITARM'])/'bin/arm-none-eabi-')
  with(job/'symbols.txt').open('w')as f:subprocess.run([prefix+'nm','-n',str(job/(target+'.elf'))],stdout=f,check=True)
  m=verify_rom(job/'assets',job/(target+'.gba'),job/(target+'.elf'),revision)
 else:
  m=json.loads((work/'collection-input/verified-collection.json').read_text())
  image=(work/'scripts/toolchain-image.txt').read_text().strip()
  with(job/'symbols.txt').open('w')as f:subprocess.run(['docker','run','--rm','-v',str(job)+':/candidate:ro',image,'/opt/devkitpro/devkitARM/bin/arm-none-eabi-nm','-n','/candidate/'+target+'.elf'],stdout=f,check=True)
 graphics={}
 for header in (work/'build').glob('*.h'):
  for name,size in re.findall(r'#define (\w+(?:Tiles|Map|Pal))Len (\d+)',header.read_text()):
   graphics[name]=int(size)
 m['generated_graphics_bytes']=graphics
 m.update(schema='gba-collection-candidate-v1',rom=target+'.gba',elf=target+'.elf',source_tree_sha256=source['source_tree_sha256'],release_promotion='blocked; documented ordinary-output limitation',hardware_verified=False)
 m['file_sha256']={name:file_hash(job/name)for name in [m['rom'],m['elf'],'symbols.txt']}
 (job/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 _,end=source_snapshot(root)
 if end!=source:raise ValueError('Source changed during build')
 (root/'builds/m022-candidates'/profile/'LATEST.txt').write_text(str(job.relative_to(root))+'\n')
 print(json.dumps(dict(build=str(job),source_commit=revision,rom_sha256=m['rom_sha256'],bytes=m['rom_bytes']),indent=2));return job
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,default=Path(__file__).absolute().parents[1]);p.add_argument('--spec',type=Path,required=True);p.add_argument('--native',action='store_true');a=p.parse_args();build(a.repo,json.loads(a.spec.read_text()),a.native)
