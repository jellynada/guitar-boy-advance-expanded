"""Measure linked song costs; project storage capacity without changing music."""
import argparse,json,os,re,struct,subprocess
from pathlib import Path
LIMIT=32*1024**2
def union(spans):
 spans=sorted(spans);total=0;end=0
 for a,b in spans:
  if b>a:total+=max(0,b-max(a,end));end=max(end,b)
 return total
def measure(build,output,probe=None):
 build=Path(build);m=json.loads((build/'manifest.json').read_text());data=(build/m['rom']).read_bytes()
 prefix=str(Path(os.environ['DEVKITARM'])/'bin/arm-none-eabi-')
 text=subprocess.check_output([prefix+'nm','-S',str(build/m['elf'])],text=True)
 sym={n:(int(a,16)-0x08000000,int(z,16))for a,z,t,n in re.findall(r'^(\w+)\s+(\w+)\s+(\w)\s+(\S+)$',text,re.M)}
 addresses={n:int(a,16)-0x08000000 for a,t,n in re.findall(r'^(\w+)\s+(\w)\s+(\S+)$',text,re.M)}
 graphics=m.get('generated_graphics_bytes',{})
 if not graphics and (build/'engine/build').exists():
  for h in (build/'engine/build').glob('*.h'):
   graphics.update({n:int(z)for n,z in re.findall(r'#define (\w+(?:Tiles|Map|Pal))Len (\d+)',h.read_text())})
 for n,z in graphics.items():
  if n in addresses:sym[n]=(addresses[n],z)
 if 'sys8Glyphs'in addresses:sym['sys8Glyphs']=(addresses['sys8Glyphs'],768)
 section_text=subprocess.check_output([prefix+'objdump','-h',str(build/m['elf'])],text=True)
 loads=[];sections=[]
 lines=section_text.splitlines()
 for i,line in enumerate(lines):
  hit=re.match(r'\s*\d+\s+(\S+)\s+([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)\s+',line)
  if hit:
   n,z,v,l=hit.groups();size=int(z,16);v=int(v,16);l=int(l,16)
   sections.append(dict(name=n,bytes=size,vma=v,lma=l))
   if size and 'CONTENTS'in lines[i+1]and 0x08000000<=l<0x0a000000:loads.append((l-0x08000000,l-0x08000000+size))
 def string_at(offset):
  addr=struct.unpack_from('<I',data,offset)[0]-0x08000000
  if not 0<=addr<len(data):raise ValueError('Metadata string is not ROM resident')
  end=data.index(0,addr)+1;return addr,end
 cat,cat_size=sym['collectionCatalog'];desc,desc_size=sym['collectionAssets']
 if cat_size!=20*m['song_count']or desc_size!=40*m['song_count']:raise ValueError('Descriptor ABI changed')
 owned=[];songs=[]
 for s in m['songs']:
  regions=[];pcm=0;charts=0
  for a in s['audio'].values():regions.append((a['rom_offset'],a['rom_offset']+a['bytes']));pcm+=a['bytes']
  for c in s['charts']:
   for key,mul in [('notes_rom_offset',16),('holds_rom_offset',8)]:
    start=c[key];regions.append((start,start+c['count']*mul));charts+=c['count']*mul
  i=s['index'];meta=[(cat+i*20,cat+(i+1)*20),(desc+i*40,desc+(i+1)*40)]
  choices=sym['s'+str(i)+'_imported_choices'];meta.append((choices[0],choices[0]+choices[1]))
  for field in [0,4,8]:meta.append(string_at(cat+i*20+field))
  meta.append(string_at(desc+i*40+36))
  # Shared strings are counted once; report both raw referenced and unique cost.
  before=union(owned);owned.extend(regions);owned.extend(meta);increment=union(owned)-before
  songs.append(dict(index=i,id=s['id'],source_seconds=s['source_samples']/16384,guitar_bytes=s['audio']['guitar']['bytes'],backing_bytes=s['audio']['backing']['bytes'],pcm_padding_bytes=pcm-2*s['source_samples'],chart_bytes=charts,metadata_referenced_bytes=union(meta),unique_incremental_bytes=increment,shared_reference_savings_bytes=pcm+charts+union(meta)-increment,notes_by_difficulty={c['difficulty']:c['count']for c in s['charts']}))
 content=union(owned);shared=len(data)-content
 iwram=sum(s['bytes']for s in sections if 0x03000000<=s['vma']<0x03008000)
 ewram=sum(s['bytes']for s in sections if s['name']in ['.ewram','.sbss'])
 shared_code=sum(s['bytes']for s in sections if s['name']in ['.crt0','.init','.plt','.text','.fini','.iwram'])
 artnames=list(graphics)+['sys8Glyphs']
 art=[(sym[n][0],sym[n][0]+sym[n][1])for n in artnames if n in sym and sym[n][0]>=0]
 code_gap=len(data)-union(loads)
 # Planning deliberately adds the future reserve to currently measured shared bytes.
 reserve=1024**2;pad=2*(32768+8192+16384)+30
 scenarios=[]
 for seconds in [120,180,240,300]:
  variants=[]
  for chart_rate in [96,192,384]:
   per=seconds*(32768+chart_rate)+pad+256
   variants.append(dict(chart_bytes_per_second=chart_rate,per_song_bytes=per,songs=max(0,(LIMIT-reserve-shared)//per)))
  scenarios.append(dict(average_seconds=seconds,variants=variants))
 mixed=[]
 for durations in [[120,180,240,300],[180,180,240,240],[240,240,240,240],[300,300,300]]:
  total=shared+reserve+sum(t*(32768+192)+pad+256 for t in durations)
  mixed.append(dict(durations_seconds=durations,projected_total_bytes=total,fits=total<=LIMIT,remaining_bytes=LIMIT-total))
 result=dict(source_commit=m['source_commit'],rom_sha256=m['rom_sha256'],rom_bytes=len(data),ceiling_bytes=LIMIT,remaining_bytes=LIMIT-len(data),songs=songs,measured_unique_song_bytes=content,measured_shared_bytes=shared,shared_code_including_rom_loaded_iwram_bytes=shared_code,identified_shared_ui_art_bytes=union(art),shared_other_bytes=shared-shared_code-union(art),inter_section_linker_padding_bytes=code_gap,static_iwram_bytes=iwram,ewram_bytes=ewram,sections=sections,projection=dict(future_art_code_reserve_bytes=reserve,per_song_padding_allowance_bytes=pad,metadata_allowance_bytes=256,scenarios=scenarios,mixed_libraries=mixed,limitations='Projections only. Chart allowance reflects available test density, not all songs. ROM headroom is not RAM/CPU headroom. Artwork is provisional. No compression, cuts or future library has been implemented.'))
 if probe:
  probe=Path(probe);target=31*1024**2
  # Packaging-only non-ROM with explicit leading marker, no fake catalog entries.
  marker=b'M022 CAPACITY ONLY - NONPLAYABLE - NO MUSIC LIBRARY\n'
  with probe.open('xb')as f:
   f.write(marker);f.write(data);f.write(bytes(target-len(marker)-len(data)))
  result['capacity_only_probe']=dict(bytes=probe.stat().st_size,format='nonplayable binary packaging probe; not a GBA cartridge',remaining_to_32MiB=LIMIT-target,does_not_test_runtime=True)
 Path(output).write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k]for k in ['rom_bytes','remaining_bytes','measured_shared_bytes','static_iwram_bytes','ewram_bytes']},indent=2))
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--build',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--probe',type=Path);a=p.parse_args();measure(a.build,a.output,a.probe)
