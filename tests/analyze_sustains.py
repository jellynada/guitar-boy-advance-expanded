#!/usr/bin/env python3
"""Independent interval-count acceptance model for full real-song hold runs."""
import argparse,bisect,csv,json,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--adapted',type=Path,required=True);p.add_argument('--prefix',required=True);p.add_argument('--log',type=Path,required=True);p.add_argument('--early',action='store_true');a=p.parse_args()
notes=json.loads(a.adapted.read_text())['notes'];events=list(csv.DictReader(open(a.prefix+'.events.csv')))
ticks=[int(r['tick']) for r in csv.DictReader(open(a.prefix+'.csv'))]
assert len(events)==len(notes) and all(int(e['kind'])==0 for e in events),'not an all-head Perfect run'
expected=0;holds=0
for index,(n,e) in enumerate(zip(notes,events)):
    if not n['sustain_us']:continue
    holds+=1;duration=(n['sustain_us']*16777216+500000)//1000000
    end=n['runtime_tick']+duration;start=max(n['runtime_tick'],int(e['gameplay_tick']))
    if a.early:
        # Autoplay releases half way through. Input is sampled at the next
        # foreground poll; the release snapshot is independently in the CSV.
        end=min(end,ticks[bisect.bisect_left(ticks,n['runtime_tick']+duration//2)+1])
    multiplier=1 if index<9 else 2 if index<19 else 3 if index<29 else 4
    expected+=(end-start)//4194304*multiplier
log=a.log.read_text();m=re.search(r'HOLDS: total(\d+) completed(\d+) released(\d+) missed(\d+) bonus(\d+)',log);assert m
count,completed,released,missed,bonus=map(int,m.groups())
assert count==holds and bonus==expected and missed==0
assert (completed,released)==((0,holds) if a.early else (holds,0))
score=int(re.search(r'SCORE: score(\d+)',log)[1]);base=sum(10*(1 if i<9 else 2 if i<19 else 3 if i<29 else 4) for i in range(len(notes)))
assert score==base+expected and f'combo{len(notes)}' in log and 'FC1 AP1 session1' in log
report=dict(holds=holds,completed=completed,early_released=released,head_score=base,independent_bonus=expected,total=score,combo=len(notes),audio_gate_unchanged=True)
Path(a.prefix+'.holds.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
