"""Actual multi-song cartridge matrix and unchanged inherited engine oracles.
No private input discovery. --tools enables existing local Windows stock mGBA.
"""
import argparse,json,os,re,shlex,subprocess,sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from build_collection_probes import generate
ROOT=Path(__file__).resolve().parents[1]
def run(build,out,tools=None,quick=False):
 build=Path(build).absolute();out=Path(out).absolute();out.mkdir(parents=True,exist_ok=False)
 m=json.loads((build/'manifest.json').read_text())
 import hashlib
 for name,h in m.get('file_sha256',{}).items():
  if hashlib.sha256((build/name).read_bytes()).hexdigest()!=h:raise ValueError('Candidate file changed')
 data=(build/m['rom']).read_bytes()
 if hashlib.sha256(data).hexdigest()!=m['rom_sha256']:raise ValueError('Candidate ROM changed')
 sy=(build/'symbols.txt').read_text()
 symbols={v[2]:int(v[0],16)for line in sy.splitlines()if len(v:=line.split())==3}
 # These are observer names only; no aliases or changes are added to production ROM.
 for name in ['imported_notes','imported_sustain_us']:
  if name not in symbols:sy+=format(symbols['s0_'+name],'08x')+' R '+name+'\n'
 sym=out/'symbols-compat.txt';sym.write_text(sy)
 rows=[]
 for s in m['songs']:
  for c in s['charts']:
   row=[s['index'],c['lanes']-3,c['count'],s['playback_samples']]
   line=' '.join(map(str,row))+' '+' '.join(format(x,'x')for x in [0x08000000+c['notes_rom_offset'],0x08000000+c['holds_rom_offset'],0x08000000+s['audio']['guitar']['rom_offset'],0x08000000+s['audio']['backing']['rom_offset']])+' '+str(s['source_samples'])+' '+str(s['storage_samples'])
   rows.append(line)
 (out/'matrix.txt').write_text('\n'.join(rows)+'\n')
 probes=generate(ROOT,out/'probes')
 if tools:
  tools=Path(tools);cc=str(tools/'w64devkit/bin/gcc.exe')
  common=[cc,'-O2','-DBUILD_STATIC','-DM_CORE_GBA','-DUSE_DEBUGGERS','-I'+str(ROOT/'tests'),'-I'+str(tools/'mgba-0.10.5-source/include'),'-I'+str(tools/'mgba-0.10.5-build/include')]
  libs=[str(tools/'mgba-0.10.5-build/libmgba.a'),'-lws2_32','-lshlwapi','-lole32','-luuid','-lcomdlg32']
 else:common=['gcc','-O2','-I'+str(ROOT/'tests')];libs=['-lmgba']
 def compile(name,src,extra=None):
  exe=out/(name+('.exe'if tools else''));subprocess.run([*common,str(src),*(extra or []),'-o',str(exe),*libs],check=True);return exe
 binaries={}
 for n in ['pause','stress','timing','readiness','pause-trace']:binaries[n]=compile(n,probes/(n+'.c'))
 (probes/'stack.c').write_text('#define GBA_STACK_INSTRUMENT\n'+(probes/'pause.c').read_text());binaries['stack']=compile('stack',probes/'stack.c')
 binaries['multi']=compile('multi',ROOT/'tests/multi_song_emulator.c')
 if tools:
  wrap=['-Wl,--wrap='+n for n in ['GBAAudioWriteFIFO','GBAAudioSampleFIFO','GBAAudioSample','GBAIOWrite','GBAIOWrite32']]
  for n in ['pause','stress']:binaries['digital-'+n]=compile('digital-'+n,probes/(n+'.c'),[str(ROOT/'tests/windows_hardware_tap.c'),*wrap])
  tap=None
 else:
  tap=out/'tap.so';subprocess.run(['gcc','-O2','-fPIC','-shared',str(ROOT/'tests/hardware_tap.c'),'-o',str(tap),'-lmgba','-ldl'],check=True)
  for n in ['pause','stress']:binaries['digital-'+n]=binaries[n]
 jobs=[]
 for s in m['songs']:
  for position,c in enumerate(s['charts']):
   d=c['lanes']-3;folder=out/f"song-{s['index']}-difficulty-{d}";folder.mkdir()
   env=dict(os.environ,GBA_SONG=str(s['index']),GBA_DIFFICULTY=str(position),GBA_PAUSE_PLAYBACK_SAMPLES=str(s['playback_samples']))
   limit=(s['playback_samples']*1024+280895)//280896+600
   cases=[19]if quick else[0,4,11,12,17,19,20,22,23,28]
   for case in cases:
    pre=folder/f'case-{case}';args=[binaries['stress'if case in [22,23,28]else'pause'],build/m['rom'],sym,c['count'],limit,case,120 if case==20 else 1 if case==0 else 30,pre]
    jobs.append(dict(kind='gameplay',prefix=pre,args=args,env=env,song=s['index'],difficulty=d,case=case))
   if not quick:
    for mode in ['perfect','mixed']:
     pre=folder/('graphics-'+mode);jobs.append(dict(kind='graphics',prefix=pre,args=[binaries['timing'],build/m['rom'],sym,c['count'],limit,mode,pre,1],env=dict(env,GBA_REQUIRE_CLEAN_HIGHWAY='1'),song=s['index'],difficulty=d,mode=mode))
    pre=folder/'stack';jobs.append(dict(kind='stack',prefix=pre,args=[binaries['stack'],build/m['rom'],sym,c['count'],limit,12,30,pre],env=env,song=s['index'],difficulty=d))
   # Same exact FIFO oracle, established startup advance15; no lateness correction.
   for case in ([19]if quick else[19,4,22,0,12]):
    pre=folder/f'digital-{case}';denv=dict(env,GBA_HARDWARE_TAP=str(pre),GBA_TAP_MODE_ADDR=format(symbols['gameMode'],'x'),GBA_TAP_STATE_ADDR=format(symbols['audioState'],'x'),GBA_TAP_COUNT_ADDR=format(symbols['audioSamplesConsumed'],'x'),GBA_TAP_FILL_ADDR=format(symbols['_ZL12fillPosition'],'x'),GBA_TAP_NO_PWM='1')
    if tap:denv['LD_PRELOAD']=str(tap)
    jobs.append(dict(kind='digital',prefix=pre,args=[binaries['digital-stress'if case==22 else'digital-pause'],build/m['rom'],sym,c['count'],limit,case,1 if case==0 else 30,pre],env=denv,audio=build/'assets/packages'/str(s['index'])/'audio',song=s['index'],difficulty=d,case=case))
 if not quick:jobs.append(dict(kind='switching',prefix=out/'multi',args=[binaries['multi'],build/m['rom'],sym,out/'matrix.txt',out/'multi'],env=dict(os.environ)))
 def job(j):
  pre=j['prefix']
  with Path(str(pre)+'.log').open('w')as f:rc=subprocess.run(list(map(str,j['args'])),env=j['env'],stdout=f,stderr=subprocess.STDOUT).returncode
  result={k:v for k,v in j.items()if k in ['kind','song','difficulty','case','mode']};result['exit_code']=rc
  if j['kind']=='digital'and not rc:
   with Path(str(pre)+'.oracle.log').open('w')as f:result['oracle_exit_code']=subprocess.run([sys.executable,str(ROOT/'tests/analyze_fifo.py'),'--audio-dir',str(j['audio']),'--prefix',str(pre),'--startup-advance','15'],stdout=f,stderr=subprocess.STDOUT).returncode
  print(json.dumps(result),flush=True);return result
 with ThreadPoolExecutor(max_workers=3)as pool:results=list(pool.map(job,jobs))
 report=dict(source_commit=m['source_commit'],rom_sha256=m['rom_sha256'],results=results,passed=all(not r['exit_code']and not r.get('oracle_exit_code',0)for r in results))
 # Preserve ordinary-output thresholds and all original reference windows for song0.
 ordinary=[]
 if not quick:
  for s in m['songs']:
   for c in s['charts']:
    folder=out/f"song-{s['index']}-difficulty-{c['lanes']-3}"
    times='6.322,37.5,76.7'if s['provenance']=='public:synth-demo'else f"6.322,{min(136,s['source_samples']/16384/2)},{max(7,s['source_samples']/16384-2)}"
    for case in [19,4,22,0,12]:
     pre=folder/f'case-{case}';args=[sys.executable,str(ROOT/'tests/analyze_reactive.py'),'--audio-dir',str(build/'assets/packages'/str(s['index'])/'audio'),'--prefix',str(pre),'--times',times]
     if case in [4,22]:args+=['--backing-capture',str(folder/'case-23'),'--require-mute']
     if case==22:args+=['--require-recovery']
     with Path(str(pre)+'.ordinary.log').open('w')as f:rc=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT).returncode
     ordinary.append(dict(song=s['index'],difficulty=c['lanes']-3,case=case,exit_code=rc))
 if not quick and report['passed']:
  from check_pause_trace import check as check_physical_pause
  report['physical_pause_edges']=check_physical_pause(binaries['pause-trace'],build/m['rom'],sym,out/'physical-pause-edges')
  report['performance']=[dict(test=str(p.relative_to(out)),**json.loads(p.read_text()))for p in out.rglob('*.timing.json')]
  for p in report['performance']:
   if p['foreground_max']>=280896 or p['defect_frames']or p['underruns']:report['passed']=False
  report['stack_observations']=[dict(test=str(p.relative_to(out)),user_free=int(f),user_touched=int(t),irq_touched=int(i))for p in out.rglob('stack.log')for f,t,i in re.findall(r'user_free=(\d+) user_touched_from_top=(\d+) irq_touched=(\d+)',p.read_text())]
 report['ordinary_output']=dict(results=ordinary,passed=sum(not x['exit_code']for x in ordinary),total=len(ordinary),release_gate='blocked')
 (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
 return report['passed']
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--build',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--tools',type=Path);p.add_argument('--quick',action='store_true');a=p.parse_args();sys.exit(0 if run(a.build,a.output,a.tools,a.quick)else 1)
