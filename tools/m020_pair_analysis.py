"""Diagnostic of the retained Easy mixed/backing window; no acceptance changes."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import numpy as np

def rows(path):
    return list(csv.DictReader(path.open()))

def epoch(prefix,start):
    r=[x for x in rows(Path(str(prefix)+'.csv'))if x['state']=='1'and int(x['hardware_consumed'])>1000]
    indices=np.array([int(x['hardware_consumed'])-1 for x in r])
    origins=np.array([int(x['capture_samples'])-2*(int(x['hardware_consumed'])-1)for x in r])
    return int(origins[np.argmin(abs(indices-start//2))])

def find(signal,template,center):
    target=template.astype(float);target-=target.mean()
    lo=center-64;candidates=signal[lo:center+65+len(target)].astype(float)
    dots=np.correlate(candidates,target,'valid')
    sums=np.convolve(candidates,np.ones(len(target)),'valid')
    squares=np.convolve(candidates*candidates,np.ones(len(target)),'valid')
    scores=dots/np.sqrt(np.maximum(1,squares-sums*sums/len(target))*np.dot(target,target))
    index=int(np.argmax(scores));return lo+index,float(scores[index])

def run(build,captures,output):
    build,captures,output=map(Path,(build,captures,output))
    b=np.fromfile(build/'prepared/audio/imported_backing.bin',dtype=np.int8)
    # Exactly the inherited suspect window and independently measured startup.
    start=1186238;length=4096
    assert start/32768==36.20111083984375
    reference=np.r_[b[15:],np.zeros(15,dtype=np.int8)].repeat(2)
    a=captures/'difficulty-0-case-22';q=captures/'difficulty-0-case-23'
    actual=np.fromfile(str(a)+'.raw',dtype='<i2')
    baseline=np.fromfile(str(q)+'.raw',dtype='<i2')
    target_index,source_corr=find(actual,reference[start:start+length],start+epoch(a,start))
    base_index,paired_corr=find(baseline,actual[target_index:target_index+length],start+epoch(q,start))
    records=[]
    for label,suffix in [('ordinary','.raw'),('independent-blip','.replay16'),('pre-filter-PWM','.pwm16')]:
        x=np.fromfile(str(a)+suffix,dtype='<i2').astype(float)
        y=np.fromfile(str(q)+suffix,dtype='<i2').astype(float)
        ax=target_index;by=base_index
        if suffix!='.raw':
            ax+=int(Path(str(a)+'.pwm-offset.txt').read_text())
            by+=int(Path(str(q)+'.pwm-offset.txt').read_text())
        xa=x[ax:ax+length];yb=y[by:by+length]
        xa-=xa.mean();yb-=yb.mean();scale=float(np.dot(xa,yb)/np.dot(yb,yb))
        records.append(dict(layer=label,correlation=float(np.corrcoef(xa,yb)[0,1]),
            scale=scale,rms_residual=float(np.sqrt(np.mean((xa-scale*yb)**2)))))
    report=dict(diagnostic_only=True,mandatory_gate_unchanged=True,
        source_time_seconds=start/32768,window_samples=length,startup_advance_samples=15,
        target_index=target_index,reference_index=base_index,
        inherited_source_correlation=source_corr,inherited_paired_correlation=paired_corr,
        fixed_phase_residual_ms=(target_index-start-epoch(a,start))*1000/32768,
        layers=records,
        source_audio_sha256=hashlib.sha256((build/'prepared/audio/imported_backing.bin').read_bytes()).hexdigest())
    output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['build','captures','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();run(a.build,a.captures,a.output)
