#!/usr/bin/env python3
"""Pause-only continuity oracle. Existing uninterrupted acceptance stays unchanged."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyze_fifo import expected_pcm

def analyze(audio,prefix):
 events=list(csv.DictReader(open(str(prefix)+'.events.csv')))
 expected=expected_pcm(audio,events)
 samples=np.fromfile(str(prefix)+'.samples',dtype=[('segment','<u4'),('value','i1'),('cycle','<u8')]);samples=samples[samples['segment']==1]
 words=np.fromfile(str(prefix)+'.fifo',dtype=[('segment','<u4'),('end','<u4'),('word','<u4'),('cycle','<u8')]);words=words[words['segment']==1]
 assert len(samples)>1000 and len(words)>100
 advance=15 # inherited silent startup pre-roll, not fitted per run
 assert not np.any(expected[:advance])
 assert len(samples)+advance<=len(expected)
 assert np.array_equal(samples['value'],expected[advance:advance+len(samples)]),'Source samples skipped, repeated or changed'
 indices=words['end'].astype(np.int64)-4
 assert indices[0]==32 and np.all(np.diff(indices)==4),'Mixer cursor discontinuity'
 assert np.array_equal(words['word'].copy().view('i1').reshape(-1,4),expected[indices[:,None]+np.arange(4)]),'Mixed stem bytes changed'
 rows=list(csv.DictReader(open(str(prefix)+'.transport.csv')))
 stops=[];pairs=[]
 for row in rows:
  t=int(row['cycle'])
  if int(row['enabled']):
   if stops:pairs.append((stops.pop(),t))
  elif int(row['state'])==1:stops.append(t)
 # Last end-of-song stop is deliberately unpaired.
 assert pairs,'No actual pause/resume observed'
 periods=np.diff(samples['cycle'].astype(np.int64));gaps=np.flatnonzero(abs(periods-1024)>64)
 assert len(gaps)==len(pairs),(len(gaps),len(pairs))
 for i,(stop,start) in zip(gaps,pairs):
  before=int(samples['cycle'][i]);after=int(samples['cycle'][i+1])
  assert before<=stop<start<=after
  assert 0<after-start<1200,'Unexpected resumed timer interval'
  assert 0<=stop-before<1200,'Pause interrupted more than one sample interval'
 hardware=json.loads(Path(str(prefix)+'.hardware.json').read_text());assert hardware['paused_fifo_requests']==0
 assert hardware['late_last_words']==hardware['late_blend_writes']==0
 return dict(consumed_samples_checked=len(samples),mixer_words_checked=len(words),digital_mismatches=0,mixer_mismatches=0,pause_gaps=len(pairs),paused_fifo_requests=0,startup_advance=advance,max_boundary_fraction_cycles=1024,meaning='Every consumed/written sample checked against independent two-stem mixer; explicit transport gaps only. Not an analog click-free claim.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--audio-dir',type=Path,required=True);p.add_argument('--prefix',type=Path,required=True);a=p.parse_args();result=analyze(a.audio_dir,a.prefix);Path(str(a.prefix)+'.continuity.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
