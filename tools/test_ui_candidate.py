"""Actual-candidate UI, inherited gameplay, graphics, stack and audio-output checks.
No release waiver: the strict audio comparator still exits nonzero on failures.
"""
import argparse,json,os,subprocess,sys,re,shlex
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.build_ui_candidate import verify
from tools.release_common import file_hash
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from build_ui_probes import generate

PUBLIC_OUTPUT_TIMES = '6.322,37.5,76.7'  # Original check_demo_audio public reference windows.

def run(build,output,cc='gcc',flags='',output_only=False):
 root=Path(__file__).resolve().parents[1];build=Path(build).resolve();output=Path(output).resolve();m=verify(build);rom=build/m['rom'];prepared=json.loads((build/'prepared/song-manifest.json').read_text());counts=[c['note_heads']for c in prepared['runtime']['difficulties']]
 if len(counts)!=3:raise ValueError('M021 review matrix requires all three supported difficulties')
 limit=(prepared['audio']['playback_samples']*1024+280895)//280896+600
 if not output_only:
  output.mkdir(parents=True,exist_ok=False);probes=generate(root,output/'probes');common=[cc,'-O2','-Wall','-Wextra',*shlex.split(flags)];libs=['-lmgba']
  for name,src in [('pause',probes/'pause.c'),('stress',probes/'stress.c'),('timing',probes/'timing.c'),('readiness',probes/'readiness.c'),('physical',probes/'physical.c'),('pause-trace',probes/'pause-trace.c'),('ui',root/'tests/ui_navigation_emulator.c')]:subprocess.run([*common,'-I'+str(root/'tests'),str(src),'-o',str(output/name),*libs],check=True)
  # Only writes unused stack canaries, as in the retained stack observer.
  stack='#define GBA_STACK_INSTRUMENT\n'+(probes/'pause.c').read_text();(probes/'stack.c').write_text(stack);subprocess.run([*common,'-I'+str(root/'tests'),str(probes/'stack.c'),'-o',str(output/'stack'),*libs],check=True)
  jobs=[]
  for d,count in enumerate(counts):
   env=dict(os.environ,GBA_DIFFICULTY=str(d),GBA_PAUSE_PLAYBACK_SAMPLES=str(prepared['audio']['playback_samples']))
   for case in [0,4,11,12,17,19,20,22,23,28]:
    prefix=output/f'difficulty-{d}-case-{case}';jobs.append((prefix,[output/('stress'if case in [22,23,28]else'pause'),rom,build/'symbols.txt',count,limit,case,120 if case==20 else 1 if case==0 else 30,prefix],env))
   for mode in ['perfect','mixed']:
    prefix=output/f'graphics-{d}-{mode}';jobs.append((prefix,[output/'timing',rom,build/'symbols.txt',count,limit,mode,prefix,1],dict(env,GBA_REQUIRE_CLEAN_HIGHWAY='1')))
   prefix=output/f'stack-{d}';jobs.append((prefix,[output/'stack',rom,build/'symbols.txt',count,limit,12,30,prefix],env))
  jobs += [(output/'ui',[output/'ui',rom,build/'symbols.txt',*counts,limit,output/'ui'],dict(os.environ))]
  jobs += [(output/'readiness',[output/'readiness',rom,build/'symbols.txt'],dict(os.environ))]
  if m['profile']=='private':jobs += [(output/'physical',[output/'physical',rom,build/'symbols.txt'],dict(os.environ))]
  def job(j):
   prefix,args,env=j
   with Path(str(prefix)+'.log').open('w')as log:rc=subprocess.run(list(map(str,args)),env=env,stdout=log,stderr=subprocess.STDOUT).returncode
   return dict(test=prefix.name,exit_code=rc)
  with ThreadPoolExecutor(max_workers=3)as pool:results=list(pool.map(job,jobs))
  performance=[json.loads((output/f'graphics-{d}-{mode}.timing.json').read_text())for d in range(3)for mode in ['perfect','mixed']if(output/f'graphics-{d}-{mode}.timing.json').exists()]
  maxima=[]
  for d in range(3):
   peaks=[int(v)for p in output.glob(f'difficulty-{d}-*.log')for v in re.findall(r'foreground_peak_cycles=(\d+)',p.read_text())]
   timings=[json.loads((output/f'graphics-{d}-{mode}.timing.json').read_text())for mode in ['perfect','mixed']]
   if len(peaks)!=10:raise ValueError('Missing foreground measurements')
   peak=max(peaks+[t['foreground_max']for t in timings]);assert peak<280896
   assert all(t['defect_frames']==t['underruns']==0 for t in timings)
   maxima.append(dict(difficulty=d,foreground_max_cycles=peak,headroom_cycles=280896-peak))
  receipt=dict(source_commit=m['source_commit'],rom_sha256=m['rom_sha256'],results=results,performance=performance,foreground=maxima,result='passed'if all(not r['exit_code']for r in results)else'failed')
  (output/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
  if receipt['result']!='passed':raise ValueError('Candidate gameplay/UI regression failed; see logs')
 else:
  observed=json.loads((output/'verification.json').read_text());assert observed['source_commit']==m['source_commit']and observed['rom_sha256']==file_hash(rom)
 # Preserve all 15 original ordinary-output assertions on this candidate.
 audio=[];times=PUBLIC_OUTPUT_TIMES if m['profile']=='public' else f"6.322,{min(136,prepared['audio']['source_samples']/16384/2)},265"
 for d in range(3):
  for case in [19,4,22,0,12]:
   prefix=output/f'difficulty-{d}-case-{case}';cmd=[sys.executable,str(root/'tests/analyze_reactive.py'),'--audio-dir',str(build/'prepared/audio'),'--prefix',str(prefix),'--times',times]
   if case in [4,22]:cmd+=['--backing-capture',str(output/f'difficulty-{d}-case-23'),'--require-mute']
   if case==22:cmd+=['--require-recovery']
   with Path(str(prefix)+'.output.log').open('w')as log:rc=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT).returncode
   audio.append(dict(difficulty=d,case=case,exit_code=rc))
 result=dict(source_commit=m['source_commit'],rom_sha256=m['rom_sha256'],results=audio,passed=sum(r['exit_code']==0 for r in audio),total=15,release_gate='blocked'if any(r['exit_code']for r in audio)else'technical-only; owner acceptance still required')
 (output/'audio-output.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--build',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--cc',default='gcc');p.add_argument('--flags',default='');p.add_argument('--output-only',action='store_true');a=p.parse_args();run(a.build,a.output,a.cc,a.flags,a.output_only)
