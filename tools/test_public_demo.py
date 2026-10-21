"""Exercise an exact built/extracted public demo using stock libmgba.

A passing gameplay receipt is NOT audio-output or hardware release clearance.
Run inside the mGBA host (or --docker-container from its parent workspace).
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.build_public_demo import verify, ROM
from tools.release_common import file_hash
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from build_demo_probes import generate


def run(root, build, rom, output, container=None):
    root,build,rom,output=map(lambda p:Path(p).resolve(),(root,build,rom,output));m=verify(build)
    if file_hash(rom)!=m['rom_sha256']:raise ValueError('Test ROM is not the exact successful build')
    output.mkdir(parents=True,exist_ok=False);generate(root,output/'probes')
    def command(args,env=None,log=None):
        if container:
            cmd=['docker','exec']
            for k,v in (env or {}).items():cmd+=['-e',k+'='+str(v)]
            cmd+=[container,*map(str,args)]
            return subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
        environment={k:v for k,v in os.environ.items()if not k.startswith('GBA_')};environment.update(env or {})
        return subprocess.run(list(map(str,args)),env=environment,stdout=log,stderr=subprocess.STDOUT,check=True)
    for name,src in [('pause',output/'probes/pause.c'),('stress',output/'probes/stress.c'),('readiness',output/'probes/readiness.c'),('ui',root/'tests/demo_ui_emulator.c'),('timing',root/'tests/demo_timing_emulator.c')]:
        command(['gcc','-O2','-Wall','-Wextra','-Werror',src,'-o',output/name,'-lmgba'])
    jobs=[]
    for i,count in enumerate([86,171,335]):
        env={'GBA_DIFFICULTY':str(i),'GBA_PAUSE_PLAYBACK_SAMPLES':'1261568'}
        for case in [0,4,11,12,17,19,20,22,23]:
            prefix=output/f'difficulty-{i}-case-{case}'
            jobs.append((prefix,[output/('stress'if case in [22,23]else'pause'),rom,build/'symbols.txt',str(count),'4900',str(case),'120'if case==20 else'1'if case==0 else'30',prefix],env))
        for mode in ['perfect','mixed']:
            prefix=output/f'graphics-{i}-{mode}'
            jobs.append((prefix,[output/'timing',rom,build/'symbols.txt',str(count),'4900',mode,prefix,'1'],dict(env,GBA_REQUIRE_CLEAN_HIGHWAY='1')))
    for name in ['ui','readiness']:jobs.append((output/name,[output/name,rom,build/'symbols.txt'],{}))
    def job(item):
        prefix,args,env=item
        try:
            with Path(str(prefix)+'.log').open('w')as log:command(args,env,log)
            return dict(test=prefix.name,exit_code=0)
        except subprocess.CalledProcessError as error:
            return dict(test=prefix.name,exit_code=error.returncode)
    with ThreadPoolExecutor(max_workers=3)as pool:passed=list(pool.map(job,jobs))
    failures=[r for r in passed if r['exit_code']]
    if failures:
        (output/'FAILED.json').write_text(json.dumps(failures,indent=2)+'\n');raise RuntimeError('Emulator checks failed; inspect FAILED.json and individual logs')
    maxima=[]
    for i in range(3):
        timings=[json.loads((output/f'graphics-{i}-{mode}.timing.json').read_text())for mode in ['perfect','mixed']]
        peaks=[int(v)for p in output.glob(f'difficulty-{i}-*.log')for v in re.findall('foreground_peak_cycles=(\\d+)',p.read_text())]
        maximum=max(peaks+[t['foreground_max']for t in timings]);assert maximum<280896,('frame deadline',i,maximum)
        assert all(t['defect_frames']==0 and t['underruns']==0 for t in timings)
        maxima.append(dict(difficulty=i,foreground_max_cycles=maximum,frame_cycles=280896,headroom_cycles=280896-maximum,graphics=timings))
    receipt=dict(source_commit=m['source_commit'],rom_sha256=file_hash(rom),passed=passed,performance=maxima,result='passed',audio_output_release_gate='separate; not cleared by gameplay tests',hardware_verified=False)
    (output/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2));return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--build',type=Path,required=True);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--docker-container');a=p.parse_args();run(a.repo,a.build,a.rom,a.output,a.docker_container)
