#!/usr/bin/env python3
"""Original Easy/Medium/Hard package for actual menu/input testing."""
import argparse
from pathlib import Path
try:
    from .generate_song_examples import generate
except ImportError:
    from generate_song_examples import generate

def generate_difficulties(output):
    pulse,_=generate(output)
    chart=pulse/'notes.chart'
    medium=[(i*192,l,96 if i==2 else 1) for i,l in enumerate([0,1,2,3,0,1,2,3])]+[(1536,2,1),(1536,3,1)]
    hard=[(i*192,l,384 if i==1 else 96 if i in (4,7) else 1) for i,l in enumerate([0,1,2,3,4,1,1,4,3,2])]+[(1920,1,96),(1920,3,96),(1920,4,96)]
    with chart.open('a') as f:
        for name,notes in [('MediumSingle',medium),('HardSingle',hard)]:
            f.write('['+name+']\n{\n'+''.join(f'{t} = N {lane} {duration}\n' for t,lane,duration in notes)+'}\n')
    return pulse

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output',type=Path)
    print(generate_difficulties(p.parse_args().output))
