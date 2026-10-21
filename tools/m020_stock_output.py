"""Focused stock-output experiment; all original release gates stay unchanged.

Generate only a host AV observer around the existing Easy mixed/backing probes.
Compare an independent blip replay with ordinary output using the measured
discarded-sample offset, with no searching, gain fit, or changed thresholds.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from build_demo_probes import generate

def run(build,output,cc,flags,tap=False):
    root=Path(__file__).resolve().parents[1]
    build,output=Path(build).resolve(),Path(output).resolve()
    output.mkdir(parents=True,exist_ok=False)
    generate(root,output/'probes')
    source=(output/'probes/stress.c').read_text()
    source=source.replace('static FILE* captured,*captureCsv;',
        'static FILE* captured,*captureCsv;\n#include "m020_pwm_observer.h"')
    old='if(!i&&captured){fwrite(b,2,n,captured);captureWritten+=n;}'
    assert source.count(old)==1
    source=source.replace(old,old+'else if(!i){m020Discarded+=n;}')
    old='c->reset(c);'
    assert source.count(old)==1
    source=source.replace(old,'m020Init(c,argv[7]);'+old)
    old='captured=fopen(file,"wb");'
    assert source.count(old)==1
    source=source.replace(old,'m020Offset(argv[7]);'+old)
    (output/'observer.c').write_text(source)
    common=[cc,'-O2','-Wall','-Wextra','-Werror','-I'+str(root/'tests'),*flags]
    subprocess.run([*common,str(output/'observer.c'),'-o',str(output/'observer'),'-lmgba'],check=True)
    subprocess.run([*common,str(root/'tests/m020_blip_reference.c'),'-o',str(output/'reference'),'-lmgba'],check=True)
    if tap:
        subprocess.run([*common,'-fPIC','-shared',str(root/'tests/m020_fifo_observer.c'),'-o',str(output/'tap.so'),'-lmgba','-ldl'],check=True)
    symbols={v[2]:v[0]for line in(build/'symbols.txt').read_text().splitlines()if len(v:=line.split())==3}
    manifest=json.loads((build/'manifest.json').read_text())
    rom=build/manifest['rom']
    assert hashlib.sha256(rom.read_bytes()).hexdigest()==manifest['rom_sha256']
    records=[]
    for case in [22,23]:
        prefix=output/f'difficulty-0-case-{case}'
        env={k:v for k,v in os.environ.items()if not k.startswith('GBA_')}
        env.update(GBA_DIFFICULTY='0',GBA_PAUSE_PLAYBACK_SAMPLES='1261568')
        if tap:
            env.update(LD_PRELOAD=str(output/'tap.so'),GBA_HARDWARE_TAP=str(prefix),
                GBA_TAP_MODE_ADDR=symbols['gameMode'],GBA_TAP_STATE_ADDR=symbols['audioState'],
                GBA_TAP_COUNT_ADDR=symbols['audioSamplesConsumed'],GBA_TAP_FILL_ADDR=symbols['_ZL12fillPosition'],GBA_TAP_NO_PWM='1')
        with Path(str(prefix)+'.log').open('w')as log:
            subprocess.run([str(output/'observer'),str(rom),str(build/'symbols.txt'),'86','4900',str(case),'30',str(prefix)],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
        subprocess.run([str(output/'reference'),str(prefix)+'.pwm16',str(prefix)+'.replay16'],check=True)
        actual=np.fromfile(str(prefix)+'.raw',dtype='<i2')
        replay=np.fromfile(str(prefix)+'.replay16',dtype='<i2')
        offset=int(Path(str(prefix)+'.pwm-offset.txt').read_text())
        predicted=replay[offset:offset+len(actual)]
        assert len(predicted)==len(actual),(len(predicted),len(actual),offset)
        different=int(np.count_nonzero(actual!=predicted))
        record=dict(case=case,offset=offset,samples=len(actual),mismatches=different,
            maximum_error=int(np.max(np.abs(actual.astype(np.int32)-predicted))),
            raw_sha256=hashlib.sha256(actual.tobytes()).hexdigest(),
            predicted_sha256=hashlib.sha256(predicted.tobytes()).hexdigest())
        records.append(record)
    result=dict(source_commit=manifest['source_commit'],rom_sha256=manifest['rom_sha256'],
        diagnostic_only=True,release_gate_unchanged=True,records=records,
        independent_output_replay_exact=all(r['mismatches']==0 for r in records))
    (output/'pwm-replay.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--build',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    p.add_argument('--cc',default='gcc');p.add_argument('--flag',action='append',default=[])
    p.add_argument('--tap',action='store_true')
    a=p.parse_args();run(a.build,a.output,a.cc,a.flag,a.tap)
