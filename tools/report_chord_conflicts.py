#!/usr/bin/env python3
"""Read-only native-chart conflict report. Never adapts or writes song content."""
import argparse,json
from pathlib import Path
try:
    from .song_package import inspect
except ImportError:
    from song_package import inspect
LAYOUTS={'Medium':['LEFT','RIGHT','B','A'],'Hard':['LEFT','UP/DOWN','RIGHT','B','A']}
def report(song):
    result=[];cutoff=(song['resolution']+2)//3
    for track in song['tracks']:
        difficulty=track['difficulty']
        if difficulty not in LAYOUTS or track['instrument']!='five_fret_lead_guitar':continue
        buttons=LAYOUTS[difficulty];opposite=1 if difficulty=='Medium'else 2;groups={}
        for i,n in enumerate(track['notes']):groups.setdefault(n['start_us'],[]).append((i,n))
        active={};head_conflicts=[];hold_conflicts=[];maximum=0
        def describe(item):
            i,n=item;lane=n['lane'];return dict(index=i,source_tick=n['tick'],lane=lane,button=buttons[lane]if lane is not None and lane<len(buttons)else'unsupported',end_us=n['end_us'],genuine_sustain=n['duration_ticks']>=cutoff and n['duration_us']>0)
        for time,items in sorted(groups.items()):
            active={lane:item for lane,item in active.items()if item[1]['end_us']>time}
            fresh={n['lane']for _,n in items};maximum=max(maximum,len(items))
            simultaneous={0,opposite}<=fresh
            held_pair=(0 in fresh and opposite in active)or(opposite in fresh and 0 in active)
            if simultaneous or held_pair:
                row=dict(source_us=time,runtime_us=time+2000000,heads=[describe(x)for x in items],held=[describe(x)for _,x in sorted(active.items())])
                if simultaneous:head_conflicts.append(row)
                if held_pair:hold_conflicts.append(row)
            for item in items:
                n=item[1]
                if n['duration_ticks']>=cutoff and n['duration_us']>0:active[n['lane']]=item
        result.append(dict(difficulty=difficulty,note_heads=len(track['notes']),maximum_chord_heads=maximum,simultaneous_opposing_chords=head_conflicts,opposing_hold_interactions=hold_conflicts))
    return dict(policy='report-only; native chart unchanged; runtime includes existing2s pre-roll',charts=result)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('package',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();song,_=inspect(a.package,[]);data=report(song)
    with a.output.open('x')as f:f.write(json.dumps(data,indent=2)+'\n')
