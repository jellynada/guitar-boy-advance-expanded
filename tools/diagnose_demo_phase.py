"""Isolated startup-phase experiment, never an acceptance analyzer.

It keeps correlation/leakage/time limits unchanged, but uses the independent
consumed-byte oracle's fixed15-sample phase in a separate expected waveform.
The original mandatory check_demo_audio gate is NOT replaced or cleared.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def run(root,build,captures,digital,output):
    root,build,captures,digital,output=map(lambda p:Path(p).resolve(),(root,build,captures,digital,output))
    b=json.loads((build/'manifest.json').read_text());d=json.loads(digital.read_text());g=json.loads((captures/'verification.json').read_text())
    assert d['passed'] and d['startup_advance_samples']==15
    assert all(x['rom_sha256']==b['rom_sha256']and x['source_commit']==b['source_commit']for x in [d,g])
    source=(root/'tests/analyze_reactive.py').read_text();output.mkdir(parents=True,exist_ok=False)
    for old,new in [('reference=expected.astype(float).repeat(2)','reference=np.r_[expected[15:],np.zeros(15)].astype(float).repeat(2)'),('guitar_reference=g.astype(float).repeat(2);backing_reference=b.astype(float).repeat(2)','guitar_reference=np.r_[g[15:],np.zeros(15)].astype(float).repeat(2);backing_reference=np.r_[b[15:],np.zeros(15)].astype(float).repeat(2)')]:
        assert source.count(old)==1;source=source.replace(old,new)
    script=output/'known-fifo-phase.py';script.write_text(source)
    for p in captures.iterdir():
        if p.suffix in ['.raw','.csv']:(output/p.name).symlink_to(p)
    results=[]
    for difficulty in range(3):
        for case in [19,4,22,0,12]:
            prefix=output/f'difficulty-{difficulty}-case-{case}'
            args=[sys.executable,str(script),'--audio-dir',str(build/'prepared/audio'),'--prefix',str(prefix),'--times','6.322,37.5,76.7']
            if case in [4,22]:args+=['--backing-capture',str(output/f'difficulty-{difficulty}-case-23'),'--require-mute']
            if case==22:args+=['--require-recovery']
            with Path(str(prefix)+'.log').open('w')as f:rc=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT).returncode
            results.append(dict(difficulty=difficulty,case=case,exit_code=rc))
    report=dict(source_commit=b['source_commit'],rom_sha256=b['rom_sha256'],diagnostic_only=True,mandatory_gate_unchanged=True,phase_samples=15,script_sha256=hashlib.sha256(script.read_bytes()).hexdigest(),passed=sum(x['exit_code']==0 for x in results),total=15,results=results)
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1])
    for n in ['build','captures','digital','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();run(a.repo,a.build,a.captures,a.digital,a.output)
