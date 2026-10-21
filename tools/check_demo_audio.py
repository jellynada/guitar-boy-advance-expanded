"""Keep strict public-demo output failures visible (nonzero exit is a release gate).

Uses captures from test_public_demo.py; a real wrong press during count-in
provides a genuinely muted independent backing reference (case23).
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys


def check(root, build, captures):
    root,build,captures=map(Path,(root,build,captures));results=[]
    try:
        from .build_public_demo import verify
    except ImportError:
        from build_public_demo import verify
    manifest=verify(build);observed=json.loads((captures/'verification.json').read_text())
    if any(manifest[k]!=observed[k]for k in ['source_commit','rom_sha256']):raise ValueError('Stale or foreign audio captures')
    for difficulty in range(3):
        for case in [19,4,22,0,12]:
            prefix=captures/f'difficulty-{difficulty}-case-{case}'
            cmd=[sys.executable,str(root/'tests/analyze_reactive.py'),'--audio-dir',str(build/'prepared/audio'),'--prefix',str(prefix),'--times','6.322,37.5,76.7']
            if case in [4,22]:cmd+=['--backing-capture',str(captures/f'difficulty-{difficulty}-case-23'),'--require-mute']
            if case==22:cmd+=['--require-recovery']
            with Path(str(prefix)+'.output.log').open('w')as log:rc=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT).returncode
            results.append(dict(difficulty=difficulty,case=case,exit_code=rc))
    report=dict(source_commit=manifest['source_commit'],rom_sha256=manifest['rom_sha256'],check='ordinary unmodified mGBA output; existing thresholds unchanged',passed=sum(r['exit_code']==0 for r in results),total=len(results),results=results,release_gate='passed'if all(r['exit_code']==0 for r in results)else'blocked')
    (captures/'audio-output.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return all(r['exit_code']==0 for r in results)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--build',type=Path,required=True);p.add_argument('--captures',type=Path,required=True);a=p.parse_args();sys.exit(0 if check(a.repo,a.build,a.captures)else 1)
