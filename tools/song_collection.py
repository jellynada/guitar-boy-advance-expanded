"""Explicit, provenance-checked ROM collection generation. No directory discovery.
Public inputs are fixed original generators; private inputs require explicit paths.
"""
import argparse,hashlib,json,re,shutil,subprocess,sys,tempfile
from pathlib import Path
try:
 from .song_pipeline import prepare,verify_prepared
 from .compose_public_demo import generate
 from .chart_importer import normalize
 from .adapt_chart import adapt,header
 from .reactive_prepare import synthetic_reactive
except ImportError:
 from song_pipeline import prepare,verify_prepared
 from compose_public_demo import generate
 from chart_importer import normalize
 from adapt_chart import adapt,header
 from reactive_prepare import synthetic_reactive
RATE=16384
LIMIT=32*1024**2
PUBLIC={
 'public:synth-demo':('copper-circuit','Synth Demo','Original composition'),
 'public:synth-demo-2':('synthetic-easy-fixture','Synth Demo 2','Original test fixture'),
}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n',encoding='utf8')
def validate(spec):
 if set(spec)!={'schema','profile','entries'} or spec['schema']!='gba-song-collection-v1' or spec['profile']not in ('public','private'):raise ValueError('Invalid collection schema/profile')
 entries=spec['entries']
 if not isinstance(entries,list)or not 2<=len(entries)<=32:raise ValueError('Collection needs 2..32 explicit entries')
 ids=set();refs=set()
 for e in entries:
  if not isinstance(e,dict)or set(e)not in ({'id','package'},{'id','package','prepared'}):raise ValueError('Malformed entry')
  if not isinstance(e['id'],str)or not re.fullmatch('[a-z][a-z0-9-]{0,47}',e['id'])or e['id']in ids:raise ValueError('Missing/duplicate/invalid song ID')
  ids.add(e['id'])
  p=e['package']
  if p in PUBLIC:
   if set(e)!={'id','package'}or e['id']!=PUBLIC[p][0]:raise ValueError('Public generator identity cannot be overridden')
   ref=p
  elif p=='private:prepared'and spec['profile']=='private':
   if not isinstance(e.get('prepared'),str):raise ValueError('Explicit private prepared directory required')
   ref=str(Path(e['prepared']).resolve()).lower()
  else:raise ValueError('Unauthorized content/profile')
  if ref in refs:raise ValueError('Duplicate asset reference')
  refs.add(ref)
 return spec
def public_package(key,dest):
 root=Path(__file__).resolve().parents[1]
 if key=='public:synth-demo':
  generate(dest.parent/('composition-'+dest.name))
  prepare(dest.parent/('composition-'+dest.name),dest,difficulty='All',guitar='guitar.wav',backing=['backing.wav'],max_duration=75,handheld=True,display_title='Copper Circuit')
  verify_prepared(dest)
 elif key=='public:synth-demo-2':
  dest.mkdir(parents=True);song=normalize((root/'tests/fixtures/runtime/easy.chart').read_text(),'Synthetic Easy Test')
  (dest/'imported_chart.hpp').write_text(header(adapt(song,difficulty='Easy',instrument='five_fret_lead_guitar',synthetic=True)))
  synthetic_reactive(song,dest/'audio')
 else:raise ValueError('Unallowlisted public generator')
 return dest
def inspect_package(folder):
 folder=Path(folder);text=(folder/'imported_chart.hpp').read_text();a=json.loads((folder/'audio/audio.json').read_text())
 # Reuse the independent strict format/padding/headroom/chart-binding validator.
 with tempfile.TemporaryDirectory()as tmp:
  t=Path(tmp);shutil.copyfile(folder/'imported_chart.hpp',t/'imported_chart.hpp')
  subprocess.run([sys.executable,str(Path(__file__).with_name('build_audio.py')),'--output-dir',str(t),'--audio-dir',str(folder/'audio')],check=True,capture_output=True)
 counts=[]
 if 'GBA_IMPORTED_CHOICES'in text:
  for notes,holds,count,lanes,name in re.findall(r'\{(\w+),(\w+),(\d+),(\d+),"(Easy|Medium|Hard)"\}',text):
   if int(lanes)!={'Easy':3,'Medium':4,'Hard':5}[name]:raise ValueError('Invalid lanes')
   counts.append(dict(notes=notes,holds=holds,count=int(count),lanes=int(lanes),difficulty=name))
 else:
  n=re.search(r'imported_note_count = (\d+)',text)
  if n:counts=[dict(notes='imported_notes',holds='imported_sustain_us',count=int(n[1]),lanes=3,difficulty='Easy')]
 if not counts or len({c['difficulty']for c in counts})!=len(counts)or any(not 0<c['count']<=8192 for c in counts):raise ValueError('Missing/invalid charts')
 if a['sample_rate']!=RATE or a['schema_version']!='gba-reactive-audio-v1':raise ValueError('Collection requires independent 16384Hz stems')
 g=folder/'audio/imported_audio.bin';b=folder/'audio/imported_backing.bin'
 if not a['source_samples']or not a['playback_samples']or g.stat().st_size!=b.stat().st_size:raise ValueError('Unaligned stem boundaries')
 return text,a,counts
def generate_collection(spec,out):
 validate(spec);out=Path(out);out.mkdir(parents=True,exist_ok=False);(out/'audio').mkdir()
 songs=[];headers=[];max_count=0;largest=None
 for i,e in enumerate(spec['entries']):
  folder=out/'packages'/str(i)
  if e['package']in PUBLIC:
   public_package(e['package'],folder);_,title,artist=PUBLIC[e['package']]
   provenance=e['package']
  else:
   verify_prepared(e['prepared']);shutil.copytree(e['prepared'],folder)
   meta=json.loads((folder/'normalized-song.json').read_text())['metadata']
   title=meta['Name'];artist=meta.get('Artist','');provenance='owner-local-verified-prepared'
  if not all(isinstance(s,str)and 0<len(s)<=127 and all(32<=ord(c)<=126 for c in s)for s in [title])or not isinstance(artist,str)or len(artist)>127:raise ValueError('Invalid metadata')
  text,a,counts=inspect_package(folder)
  prefix='s'+str(i)+'_'
  renamed=re.sub(r'\b(?:imported_|chart_)\w+',lambda m:prefix+m[0],text)
  renamed='\n'.join(line for line in renamed.splitlines()if not line.startswith(('#include','#pragma','#define')))
  if 'GBA_IMPORTED_CHOICES'not in text:
   renamed+='\ninline constexpr ImportedChartChoice '+prefix+'imported_choices[]={{'+prefix+'imported_notes,'+prefix+'imported_sustain_us,'+str(counts[0]['count'])+',3,"Easy"}};\n'
  headers.append(renamed)
  for c in counts:
   c['notes_symbol']=prefix+c['notes'];c['holds_symbol']=prefix+c['holds']
   if c['count']>max_count:max_count=c['count'];largest=(prefix+c['notes'],prefix+c['holds'])
  mask=sum(1<<(c['lanes']-3)for c in counts)
  inventory={}
  for role,name in [('guitar','imported_audio.bin'),('backing','imported_backing.bin')]:
   target='s'+str(i)+'_'+role+'.bin';shutil.copyfile(folder/'audio'/name,out/'audio'/target)
   inventory[role]=dict(file=target,symbol=target.replace('.','_'),bytes=(out/'audio'/target).stat().st_size,sha256=sha(out/'audio'/target))
  songs.append(dict(index=i,id=e['id'],title=title,artist=artist,provenance=provenance,source_samples=a['source_samples'],playback_samples=a['playback_samples'],storage_samples=inventory['guitar']['bytes'],sample_rate=RATE,difficulty_mask=mask,charts=counts,cut='GBA_IMPORTED_CUT'in text,chart_header_sha256=sha(folder/'imported_chart.hpp'),audio=inventory,package_inventory={p.relative_to(folder).as_posix():sha(p)for p in folder.rglob('*')if p.is_file()}))
 total=sum(x['bytes']for s in songs for x in s['audio'].values())
 if total>=LIMIT:raise ValueError('Song payload exceeds cartridge limit')
 chart='#pragma once\n#include "note.h"\n#include "importedChoice.hpp"\n#include <cstdint>\n'+'\n'.join(headers)
 chart+='\n#define GBA_IMPORTED_CHOICES 1\ninline constexpr uint32_t imported_note_count = '+str(max_count)+';\ninline constexpr auto& imported_notes='+largest[0]+';\ninline constexpr auto& imported_sustain_us='+largest[1]+';\ninline constexpr auto& imported_choices=s0_imported_choices;\n'
 chart+='inline constexpr const char* imported_title="Collection";\n'
 (out/'imported_chart.hpp').write_text(chart)
 (out/'imported_audio.hpp').write_text('#pragma once\n#include "pcmSource.hpp"\ninline constexpr bool imported_audio_enabled=true,imported_audio_reactive=true;\ninline constexpr uint32_t imported_audio_rate=16384;\n#define imported_audio_source_samples (activePcm.sourceSamples)\n#define imported_audio_playback_samples (activePcm.playbackSamples)\n')
 (out/'ui_song.hpp').write_text('#pragma once\n')
 cpp='#pragma once\n#include "songAssets.hpp"\n#include "imported_chart.hpp"\nextern "C" {\n'
 for s in songs:
  for a in s['audio'].values():cpp+='extern const unsigned char '+a['symbol']+'[];\n'
 cpp+='}\ninline const UiNav::Song collectionCatalog[]={\n'
 for s in songs:cpp+='{'+','.join([json.dumps(s['id']),json.dumps(s['title']),json.dumps(s['artist']),str(s['source_samples']//RATE),str(s['difficulty_mask']),'true',str(s['index']+1)])+'},\n'
 cpp+='};\ninline const SongAssets collectionAssets[]={\n'
 for s in songs:
  i=s['index'];cpp+='{&collectionCatalog['+str(i)+'],s'+str(i)+'_imported_choices,'+str(len(s['charts']))+',{'+s['audio']['guitar']['symbol']+','+s['audio']['backing']['symbol']+','+str(s['source_samples'])+','+str(s['playback_samples'])+','+str(s['storage_samples'])+'},'+str(s['cut']).lower()+','+json.dumps(s['chart_header_sha256'])+'},\n'
 cpp+='};\ninline constexpr unsigned collectionSongCount='+str(len(songs))+';\n'
 (out/'song_collection.hpp').write_text(cpp)
 manifest=dict(schema='gba-collection-assets-v1',profile=spec['profile'],song_count=len(songs),maximum_chart_heads=max_count,pcm_payload_bytes=total,songs=songs)
 save(out/'collection.json',manifest);return manifest
def verify_rom(folder,rom,elf,revision):
 folder,rom,elf=map(Path,(folder,rom,elf));m=json.loads((folder/'collection.json').read_text());data=rom.read_bytes()
 if len(data)>LIMIT or data[0xB2]!=0x96 or (sum(data[0xA0:0xBD])+0x19+data[0xBD])&255:raise ValueError('Invalid cartridge size/header')
 import os,struct
 prefix=str(Path(os.environ['DEVKITARM'])/'bin/arm-none-eabi-')
 sy=subprocess.check_output([prefix+'nm','-S',str(elf)],text=True)
 symbols={n:(int(a,16),int(size,16))for a,size,t,n in re.findall(r'^(\w+)\s+(\w+)\s+(\w)\s+(\S+)$',sy,re.M)}
 def embedded(symbol,expected):
  if symbol not in symbols:raise ValueError('Missing asset symbol: '+symbol)
  addr,size=symbols[symbol];offset=addr-0x08000000
  if offset<192 or offset+len(expected)>len(data)or size!=len(expected)or data[offset:offset+len(expected)]!=expected:raise ValueError('Embedded asset mismatch: '+symbol)
  return offset
 regions=[]
 for s in m['songs']:
  folder_song=folder/'packages'/str(s['index'])
  for n,h in s['package_inventory'].items():
   if sha(folder_song/n)!=h:raise ValueError('Prepared package changed')
  text,a,counts=inspect_package(folder_song)
  for role,v in s['audio'].items():
   blob=(folder/'audio'/v['file']).read_bytes()
   if hashlib.sha256(blob).hexdigest()!=v['sha256']:raise ValueError('Audio inventory changed')
   off=embedded(v['symbol'],blob);regions.append((off,off+len(blob)))
   v['rom_offset']=off
  for c in s['charts']:
   note_body=re.search(r'\b'+c['notes']+r'\[\] = \{(.*?)\};',text,re.S)
   hold_body=re.search(r'\b'+c['holds']+r'\[\] = \{(.*?)\};',text,re.S)
   if not note_body or not hold_body:raise ValueError('Unverified chart encoding')
   notes=b''.join(struct.pack('<QII',int(t),int(l),int(d))for t,l,d in re.findall(r'\{(\d+)ULL, (\d+)U, (\d+)U\}',note_body[1]))
   holds=b''.join(struct.pack('<Q',int(v))for v in re.findall(r'(\d+)ULL',hold_body[1]))
   if len(notes)!=c['count']*16 or len(holds)!=c['count']*8:raise ValueError('Chart extent mismatch')
   c['notes_rom_offset']=embedded(c['notes_symbol'],notes);c['holds_rom_offset']=embedded(c['holds_symbol'],holds)
   c['chart_bytes']=len(notes)+len(holds)
   c['notes_sha256']=hashlib.sha256(notes).hexdigest();c['holds_sha256']=hashlib.sha256(holds).hexdigest()
 for (a,b),(c,d) in zip(sorted(regions),sorted(regions)[1:]):
  if b>c:raise ValueError('Overlapping PCM payloads')
 marker=('GBA_BUILD:M022:collection-'+m['profile']+':'+revision).encode()+b'\0'
 if data.count(marker)!=1:raise ValueError('Source/profile identity mismatch')
 with tempfile.TemporaryDirectory()as t:
  p=Path(t)/'linked.bin';subprocess.run([prefix+'objcopy','-O','binary',str(elf),str(p)],check=True);linked=p.read_bytes()
  if len(data)!=len(linked)or data[:4]!=linked[:4]or data[192:]!=linked[192:]:raise ValueError('ROM/ELF mismatch')
 m.update(source_commit=revision,rom_bytes=len(data),rom_sha256=sha(rom),elf_sha256=sha(elf),remaining_bytes=LIMIT-len(data))
 save(folder/'verified-collection.json',m);return m
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--spec',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--verify-rom',type=Path);p.add_argument('--elf',type=Path);p.add_argument('--revision');a=p.parse_args()
 if a.verify_rom:print(json.dumps(verify_rom(a.output,a.verify_rom,a.elf,a.revision),indent=2))
 else:generate_collection(json.loads(a.spec.read_text()),a.output)
