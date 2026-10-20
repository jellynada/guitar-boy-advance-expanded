#!/usr/bin/env python3
"""Run 19 actual-button scenarios for both profiles in the existing mGBA container.
Usage: python3 tests/run_pause_matrix.py /path/to/profiles.json /path/to/output
Compile pause_emulator.c as OUTPUT/pause first; symbols PROFILE.symbols required.
"""
import concurrent.futures,json,subprocess,sys
from pathlib import Path
profiles=json.loads(Path(sys.argv[1]).read_text());root=Path(sys.argv[2]).resolve()
CASES=['before-first-short','before-window','B-active','A-active','guitar-muted','B-held','A-held','BA-held','release-during-pause','new-fret-during-pause','ten-minute','START-held','eight-cycles','simultaneous-exit','START-SELECT-exit','SELECT-START-exit','paused-chord-exit','paused-SELECT-exit','last-note','uninterrupted-reference']
def run(job):
 profile,i=job;prefix=root/f'{profile}-pause-{i}';cmd=['docker','exec','mission001-mgba',str(root/'pause'),profiles[profile]['rom'],str(root/(profile+'.symbols')),'395' if profile=='cream' else '25','16400' if profile=='cream' else '1800',str(i),'36000' if i==10 else '1' if i==0 else '30',str(prefix)]
 with Path(str(prefix)+'.log').open('w')as log:rc=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT).returncode
 result=dict(profile=profile,case=i,name=CASES[i],exit_code=rc);print(result,flush=True);return result
with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:results=list(pool.map(run,[(p,i)for p in profiles for i in range(len(CASES))]))
(root/'pause-matrix.json').write_text(json.dumps(results,indent=2)+'\n');assert all(r['exit_code']==0 for r in results)
