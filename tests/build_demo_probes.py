"""Adapt only selector navigation in old assertions; public boot selects song.

All gameplay/pause/score/graphics assertions retain their original thresholds.
The separate original-profile regression suite keeps its original navigation.
"""
from pathlib import Path


def generate(root, output):
    root,output=Path(root),Path(output);output.mkdir(parents=True,exist_ok=True)
    source=(root/'tests/pause_emulator.c').read_text();old='step(c,128);step(c,0);step(c,8);step(c,0);'
    assert source.count(old)==1;source=source.replace(old,'step(c,8);step(c,0);')
    (output/'pause.c').write_text(source)
    # Dedicated, explicit stress/reference scenarios; no existing case relaxed.
    source=source.replace('cycles=test==19?0:test==12?8:1','cycles=(test==19||test==22||test==23)?0:test==12?8:1')
    source=source.replace('if(test!=4){keys|=buttons[l];','if(test!=4&&test!=23&&(test!=22||next%3!=1)){keys|=buttons[l];')
    source=source.replace('  int trigger=','  if(test==22&&frame>10&&frame%30==0){keys=0;for(unsigned lane=0;lane<lanes;++lane)keys|=buttons[lane];}\n  if(test==23&&frame==30)keys=1;\n  int trigger=')
    source=source.replace('if(test!=4){assert(c->busRead32(c,displayedStats)+','if(test==23){assert(c->busRead32(c,displayedStats+8)==count&&c->busRead32(c,displayedStats+12)==1);}\nif(test!=4&&test!=22&&test!=23){assert(c->busRead32(c,displayedStats)+')
    (output/'stress.c').write_text(source)
    source=(root/'tests/readiness_emulator.c').read_text();old='assert(c->busRead32(c,ready)==0);press(c,128);';assert old in source;source=source.replace(old,'assert(c->busRead32(c,ready)==0);');(output/'readiness.c').write_text(source)
    return output
