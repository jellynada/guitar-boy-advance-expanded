#!/usr/bin/env python3
"""Validate runtime hold lanes/durations and audio coverage before linking."""
import argparse,re
from pathlib import Path
HZ=16777216

def validate(text,audio=None):
    notes=[tuple(map(int,n)) for n in re.findall(r'\{(\d+)ULL,\s*(\d+)U,\s*(\d+)U\}',text)]
    count=int(re.search(r'imported_note_count = (\d+)',text)[1])
    lengths=[int(v) for v in re.findall(r'(\d+)ULL',text.split('imported_sustain_us[] = {',1)[1].split('}',1)[0])]
    if count>8192 or len(notes)!=count or len(lengths)!=count:raise ValueError('Hold/head array size mismatch.')
    previous=0
    for (tick,lane,unused),us in zip(notes,lengths):
        if lane>2 or tick<previous or us>7200000000:raise ValueError('Invalid Easy hold lane/order/duration.')
        previous=tick
        end=tick+(us*HZ+500000)//1000000
        if end>7203000000*HZ//1000000:raise ValueError('Hold end outside supported clock.')
        if audio is not None and end>audio:raise ValueError('Hold ends after audio EOF; resolve the source data.')
    return count,sum(bool(v) for v in lengths)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('header',type=Path);p.add_argument('--audio-header',type=Path);a=p.parse_args()
    try:
        audio=None
        if a.audio_header:
            data=a.audio_header.read_text()
            if 'imported_audio_enabled = true' in data:audio=(int(re.search(r'imported_audio_playback_samples = (\d+)',data)[1])-1)*1024
        count,holds=validate(a.header.read_text(),audio);print(f'Validated {count} Easy heads and {holds} genuine holds; lane/duration/EOF bounds pass.')
    except (ValueError,IndexError,TypeError) as e:raise SystemExit('Hold validation failed: '+str(e))
