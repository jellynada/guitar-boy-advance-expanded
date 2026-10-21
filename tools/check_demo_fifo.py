"""Digital PCM/FIFO oracle; diagnostic host tap is NEVER linked into the ROM.

Compile tests/hardware_tap.c against the SAME stock libmgba as the probes.
The established startup advance15 is explicit; no lateness correction is used.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import sys


def check(root,build,probes,output,tap,container=None,skip_pwm=False):
    root,build,probes,output,tap=map(lambda p:Path(p).resolve(),(root,build,probes,output,tap));output.mkdir(parents=True,exist_ok=False)
    from tools.build_public_demo import verify,ROM
    m=verify(build);ROM=m['rom'];sy={v[2]:v[0]for line in(build/'symbols.txt').read_text().splitlines()if len(v:=line.split())==3}
    jobs=[(d,c)for d in range(3)for c in [19,4,22,0,12]]
    def run(job):
        d,case=job;prefix=output/f'difficulty-{d}-case-{case}'
        env={'GBA_DIFFICULTY':str(d),'GBA_PAUSE_PLAYBACK_SAMPLES':'1261568','LD_PRELOAD':str(tap),'GBA_HARDWARE_TAP':str(prefix),'GBA_TAP_MODE_ADDR':sy['gameMode'],'GBA_TAP_STATE_ADDR':sy['audioState'],'GBA_TAP_COUNT_ADDR':sy['audioSamplesConsumed'],'GBA_TAP_FILL_ADDR':sy['_ZL12fillPosition']}
        if skip_pwm:env['GBA_TAP_NO_PWM']='1'
        args=[str(probes/('stress'if case==22 else'pause')),str(build/ROM),str(build/'symbols.txt'),str([86,171,335][d]),'4900',str(case),'1'if case==0 else'30',str(prefix)]
        if container:
            cmd=['docker','exec']
            for k,v in env.items():cmd+=['-e',k+'='+v]
            cmd+=[container,*args];run_env=None
        else:
            import os
            cmd=args;run_env={k:v for k,v in os.environ.items()if not k.startswith('GBA_')};run_env.update(env)
        with Path(str(prefix)+'.log').open('w')as f:rc=subprocess.run(cmd,env=run_env,stdout=f,stderr=subprocess.STDOUT).returncode
        with Path(str(prefix)+'.digital.log').open('w')as f:oracle=subprocess.run([sys.executable,str(root/'tests/analyze_fifo.py'),'--audio-dir',str(build/'prepared/audio'),'--prefix',str(prefix),'--startup-advance','15'],stdout=f,stderr=subprocess.STDOUT).returncode
        return dict(difficulty=d,case=case,process_exit_code=rc,oracle_exit_code=oracle)
    with ThreadPoolExecutor(max_workers=3)as pool:results=list(pool.map(run,jobs))
    report=dict(source_commit=m['source_commit'],rom_sha256=m['rom_sha256'],startup_advance_samples=15,results=results,passed=all(not x['process_exit_code']and not x['oracle_exit_code']for x in results),emulator_lateness_correction=False)
    (output/'digital-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return report['passed']

if __name__=='__main__':
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]));p=argparse.ArgumentParser(description=__doc__)
    for n in ['build','probes','output','tap']:p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--docker-container');p.add_argument('--skip-pwm',action='store_true',help='Omit optional PWM log only; consumed samples and FIFO words remain fully checked');a=p.parse_args();sys.exit(0 if check(a.repo,a.build,a.probes,a.output,a.tap,a.docker_container,a.skip_pwm)else 1)
