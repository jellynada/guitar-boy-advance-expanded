#!/usr/bin/env python3
"""Independent waveform/clock alignment check; optional developer NumPy dependency."""
import argparse
import csv
import json
from pathlib import Path
import wave
try:
    import numpy as np
except ImportError:
    raise SystemExit('Waveform analysis needs NumPy (Ubuntu: sudo apt install python3-numpy); building/conversion does not.')

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--pcm',type=Path,required=True)
parser.add_argument('--capture',type=Path,required=True)
parser.add_argument('--csv',type=Path,required=True)
parser.add_argument('--times',required=True,help='Runtime seconds at beginning/middle/end (includes2s pre-roll)')
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
reference=np.frombuffer(args.pcm.read_bytes(),dtype=np.int8).astype(float).repeat(2)
actual=np.fromfile(args.capture,dtype='<i2').astype(float)
rows=list(csv.DictReader(args.csv.open()))
playing=[r for r in rows if r['state']=='1' and int(r['hardware_consumed'])>1000]
if not playing:raise SystemExit('No actual playing counter samples recorded.')
# capture_samples are32.768kHz, hardware sample INDEX=count-1 at16.384kHz. Difference is
# capture start epoch, not a fitted audio delay or a VBlank song clock.
origins=np.array([int(r['capture_samples'])-2*max(0,int(r['hardware_consumed'])-1) for r in playing])
origin=int(np.median(origins))
points=[]
for time in map(float,args.times.split(',')):
    start=round(time*32768)-256
    template=reference[start:start+8000].copy();template-=template.mean()
    if len(template)<1024 or np.dot(template,template)<1:raise SystemExit('Reference window must contain actual sound.')
    guess=start+origin;lo=max(0,guess-1000)
    search=actual[lo:guess+1000+len(template)]
    if len(search)<len(template):raise SystemExit('Capture does not cover reference window.')
    dot=np.correlate(search,template,'valid')
    sums=np.convolve(search,np.ones(len(template)),'valid')
    squares=np.convolve(search*search,np.ones(len(template)),'valid')
    scores=dot/np.sqrt(np.maximum(1,squares-sums*sums/len(template))*np.dot(template,template))
    best=int(np.argmax(scores));lag=lo+best-start;error=(lag-origin)*1000/32768
    if scores[best]<0.94:raise SystemExit(f'Waveform mismatch at{time}s: correlation{scores[best]}')
    if abs(error)>3:raise SystemExit(f'Waveform/clock error{error}ms exceeds3ms.')
    points.append(dict(runtime_seconds=time,expected_event_capture_sample=round(time*32768)+origin,
                       matched_event_capture_sample=round(time*32768)+lag,
                       template_start_expected_sample=start+origin,
                       matched_capture_sample=lo+best,error_ms=error,correlation=float(scores[best])))
ended=[r for r in rows if r['state']=='2']
if ended:
    final=int(ended[-1]['tick'])
    if any(int(r['tick'])!=final for r in ended):raise SystemExit('EOF clock continued after stop.')
drift=max(p['error_ms'] for p in points)-min(p['error_ms'] for p in points)
if drift>0.2:raise SystemExit(f'Observed waveform drift{drift}ms exceeds0.2ms.')
report=dict(capture_rate=32768,hardware_rate=16384,capture_epoch_samples=origin,
            epoch_variation_samples=int(origins.max()-origins.min()),references=points,
            maximum_observed_drift_ms=drift,peak_output=int(np.abs(actual).max()),
            clipping_samples=int(np.count_nonzero(np.abs(actual)>=32767)),
            last_second_nonzero_samples=int(np.count_nonzero(actual[-32768:])))
if report['clipping_samples']:raise SystemExit('Captured output clips.')
args.output.write_text(json.dumps(report,indent=2)+'\n')
with wave.open(str(args.capture.with_suffix('.wav')),'wb') as wav:
    wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(32768);wav.writeframes(args.capture.read_bytes())
print(json.dumps(report,indent=2))
