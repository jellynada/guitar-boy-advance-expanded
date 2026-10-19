#!/usr/bin/env python3
"""Exact signed8 mixer/consumption oracle, independent of PWM/resampling quality."""
import argparse
import csv
import json
from pathlib import Path
import numpy as np


def expected_pcm(directory,events):
    guitar=np.fromfile(directory/'imported_audio.bin',dtype=np.int8).astype(np.int32)
    backing=np.fromfile(directory/'imported_backing.bin',dtype=np.int8).astype(np.int32)
    if len(guitar)!=len(backing):raise ValueError('Unaligned source streams')
    result=np.zeros(len(guitar),dtype=np.int32);position=0;gain=256;audible=True
    for event in [*events,None]:
        end=int(event['sample']) if event is not None else len(guitar)
        if not position<=end<=len(guitar):raise ValueError('Nonmonotonic event source index')
        ramp=np.arange(1,end-position+1,dtype=np.int32)*4
        ramp=np.minimum(256,gain+ramp) if audible else np.maximum(0,gain-ramp)
        result[position:end]=backing[position:end]+np.trunc(guitar[position:end]*ramp/256).astype(np.int32)
        if len(ramp):gain=int(ramp[-1])
        if event is not None:
            if int(event['gain'])!=gain:raise ValueError('Wrong event gain')
            audible=int(event['kind'])<2
        position=end
    if abs(result).max()>127:raise ValueError('Clipped independent mix')
    return result


def analyze(directory,prefix,advance):
    if not 0<=advance<=32:raise ValueError('Startup advance exceeds one FIFO capacity')
    events=list(csv.DictReader(open(str(prefix)+'.events.csv')))
    expected=expected_pcm(directory,events)
    samples=np.fromfile(str(prefix)+'.samples',dtype=[('segment','<u4'),('value','i1'),('cycle','<u8')])
    samples=samples[samples['segment']==1]
    words=np.fromfile(str(prefix)+'.fifo',dtype=[('segment','<u4'),('end','<u4'),('word','<u4'),('cycle','<u8')])
    words=words[words['segment']==1]
    if len(samples)<1000 or len(words)<100:raise ValueError('No full playback observation')
    if np.any(expected[:advance]):raise ValueError('Startup advance would discard audible content')
    n=len(samples)
    if n+advance>len(expected):raise ValueError('Consumption exceeds guarded source')
    differences=int(np.count_nonzero(samples['value']!=expected[advance:advance+n]))
    indices=words['end'].astype(np.int64)-4
    if indices[0]!=32 or np.any(np.diff(indices)!=4):raise ValueError('Skipped/repeated mixer word positions')
    if np.any(indices<0) or np.any(indices+4>len(expected)):raise ValueError('FIFO read past prepared guard')
    actual_words=words['word'].copy().view('i1').reshape(-1,4)
    word_differences=int(np.count_nonzero(actual_words!=expected[indices[:,None]+np.arange(4)]))
    if differences or word_differences:raise ValueError(f'Digital corruption: consumed={differences}, written={word_differences}')
    ticks=samples['cycle'];periods=np.diff(ticks).astype(np.int64)
    # CPU event processing overshoots a hardware boundary by a few cycles;
    # drift must still remain below one period across the complete recording.
    drift=int(ticks[-1]-ticks[0])-1024*(n-1)
    if np.any(np.abs(periods-1024)>64) or abs(drift)>64:raise ValueError('FIFO request clock discontinuity')
    return dict(consumed_samples_checked=n,mixer_words_checked=len(words),digital_mismatches=0,mixer_mismatches=0,startup_advance_samples=advance,startup_advance_ms=advance*1000/16384,request_period_min=int(periods.min()),request_period_max=int(periods.max()),complete_clock_drift_cycles=drift)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--audio-dir',type=Path,required=True);p.add_argument('--prefix',type=Path,required=True)
    p.add_argument('--startup-advance',type=int,required=True,help='Explicit bounded startup offset; never fitted per window')
    a=p.parse_args()
    try:
        report=analyze(a.audio_dir,a.prefix,a.startup_advance)
    except (OSError,ValueError) as error:raise SystemExit('FIFO analysis failed: '+str(error))
    Path(str(a.prefix)+'.digital.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
