"""Assert physical cause of case8, and no manufactured edges in pause variants."""
import argparse
import csv
import json
import os
from pathlib import Path
import subprocess


def check(probe,rom,symbols,output,container=None):
    probe,rom,symbols,output=map(lambda p:Path(p).resolve(),(probe,rom,symbols,output));output.mkdir(parents=True,exist_ok=False);results=[]
    for case in [8,24,25,27]:
        prefix=output/f'case-{case}';args=[str(probe),str(rom),str(symbols),'86','4900',str(case),'30',str(prefix)]
        if container:cmd=['docker','exec','-e','GBA_PAUSE_PLAYBACK_SAMPLES=1261568',container,*args];env=None
        else:cmd=args;env=dict(os.environ,GBA_PAUSE_PLAYBACK_SAMPLES='1261568')
        with Path(str(prefix)+'.log').open('w')as log:subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
        rows=list(csv.DictReader(open(str(prefix)+'.input.csv')));wrong=[(i,r)for i,r in enumerate(rows)if int(r['wrong'])>(int(rows[i-1]['wrong'])if i else 0)]
        if case==8:
            assert len(wrong)==1;i,r=wrong[0]
            assert int(r['raw'])==2 and int(r['physical_fresh'])==2 and r['phase_before']==r['phase_after']=='1'
            assert all(x['wrong']=='0'for x in rows[:i]);assert int(r['combo'])==0 and int(r['gate'])==0
        else:assert not wrong
        assert all(rows[i]['tick']==rows[i-1]['tick']for i in range(1,len(rows))if rows[i]['phase_before']==rows[i]['phase_after']=='2')
        results.append(dict(case=case,passed=True,wrong_events=len(wrong),cause='genuine new B press after resume; existing head already judged'if case==8 else'no manufactured press'))
    (output/'verification.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2));return results

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['probe','rom','symbols','output']:p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--docker-container');a=p.parse_args();check(a.probe,a.rom,a.symbols,a.output,a.docker_container)
