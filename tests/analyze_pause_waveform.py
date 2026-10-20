#!/usr/bin/env python3
"""Independent stem-waveform checks in declared musical windows outside pause gaps.
Boundary windows start 64 source samples after resume (3.90625ms for filter
settling), last 1024 source samples, and must finish before the next pause.
No audio correction, fitted per-window epoch, or changed uninterrupted tests.
"""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyze_fifo import expected_pcm
p=argparse.ArgumentParser();p.add_argument('--prefix',type=Path,required=True);p.add_argument('--audio-dir',type=Path,required=True);a=p.parse_args();prefix=str(a.prefix)
expected=expected_pcm(a.audio_dir,list(csv.DictReader(open(prefix+'.events.csv')))).astype(float).repeat(2)
actual=np.fromfile(prefix+'.raw',dtype='<i2').astype(float)
rows=[];stages=[];stage=0;previous='0'
for r in csv.DictReader(open(prefix+'.csv')):
 if previous=='4'and r['state']=='1':stage+=1
 previous=r['state']
 if r['state']=='1'and int(r['hardware_consumed'])>1000:rows.append(r);stages.append(stage)
stages=np.array(stages)
indices=np.array([int(r['hardware_consumed'])-1 for r in rows]);epochs=np.array([int(r['capture_samples'])-2*(int(r['hardware_consumed'])-1)for r in rows])
samples=np.fromfile(prefix+'.samples',dtype=[('segment','<u4'),('value','i1'),('cycle','<u8')]);samples=samples[samples['segment']==1];gaps=np.flatnonzero(abs(np.diff(samples['cycle'].astype(np.int64))-1024)>64)
windows=[]
for j,i in enumerate(gaps):
 source=int(i)+16 # sample after gap, plus explicit inherited15-sample startup
 windows.append((source-1088,1024,'before-pause-'+str(j),j))
 start=source+64
 assert j+1==len(gaps)or start+1024<int(gaps[j+1])+15
 windows.append((start,1024,'after-resume-'+str(j),j+1))
windows+=[(int((gaps[-1]+16+32768)),1024,'two-seconds-later',len(gaps)),(int(np.flatnonzero(expected)[-1])//2-2048,1024,'near-audible-end',len(gaps))]
report=[]
for source,length,label,stage in windows:
 start=source*2;template=expected[start:start+length*2].copy();template-=template.mean();assert np.dot(template,template)>1,(label,'silent reference')
 eligible=np.flatnonzero(stages==stage);assert len(eligible);nearest=eligible[np.argmin(abs(indices[eligible]-source))];origin=int(epochs[nearest]);guess=start+origin;lo=max(0,guess-64);search=actual[lo:guess+65+len(template)]
 assert len(search)>=len(template),label
 dots=np.correlate(search,template,'valid');s=np.convolve(search,np.ones(len(template)),'valid');sq=np.convolve(search*search,np.ones(len(template)),'valid');scores=dots/np.sqrt(np.maximum(1,sq-s*s/len(template))*np.dot(template,template));best=int(np.argmax(scores));error=(lo+best-start-origin)*1000/32768;correlation=float(scores[best]);item=dict(label=label,source_sample=source,correlation=correlation,error_ms=error);report.append(item);assert correlation>.94 and abs(error)<1,item
assert not np.any(abs(actual)>=32767)
result=dict(checks=report,excluded_boundary_filter_settling_samples=64,threshold_correlation=.94,threshold_error_ms=1);Path(prefix+'.pause-waveform.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
