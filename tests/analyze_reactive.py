#!/usr/bin/env python3
"""Compare actual mGBA output to an independent two-stem/gate waveform model."""
import argparse,csv,json,wave
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--audio-dir',type=Path,required=True);p.add_argument('--prefix',type=Path,required=True);p.add_argument('--times',default='2,9.333333,13.333333');p.add_argument('--backing-capture',type=Path,help='Independent full no-input capture for checking hardware-filtered backing');p.add_argument('--require-mute',action='store_true');p.add_argument('--require-recovery',action='store_true');a=p.parse_args()
pre=str(a.prefix);g=np.fromfile(a.audio_dir/'imported_audio.bin',dtype=np.int8).astype(np.int32);b=np.fromfile(a.audio_dir/'imported_backing.bin',dtype=np.int8).astype(np.int32);assert len(g)==len(b)
events=list(csv.DictReader(open(pre+'.events.csv')));rows=list(csv.DictReader(open(pre+'.csv')))
actual=np.fromfile(pre+'.raw',dtype='<i2').astype(float)
if a.backing_capture:
    baseline=np.fromfile(str(a.backing_capture)+'.raw',dtype='<i2').astype(float)
    br=[r for r in csv.DictReader(open(str(a.backing_capture)+'.csv')) if r['state']=='1' and int(r['hardware_consumed'])>1000]
    bi=np.array([max(0,int(r['hardware_consumed'])-1) for r in br]);be=np.array([int(r['capture_samples'])-2*max(0,int(r['hardware_consumed'])-1) for r in br])
playing=[r for r in rows if r['state']=='1' and int(r['hardware_consumed'])>1000]
assert playing,'no playing samples';epochs=np.array([int(r['capture_samples'])-2*max(0,int(r['hardware_consumed'])-1) for r in playing]);origin=int(np.median(epochs))
hardware_indices=np.array([max(0,int(r['hardware_consumed'])-1) for r in playing])
expected=np.zeros(len(g),dtype=np.int32);gains=np.zeros(len(g),dtype=np.int32);cursor=0;gain=256;audible=True;transitions=[]
def fill(end):
    global cursor,gain
    assert cursor<=end<=len(g)
    n=end-cursor
    v=np.arange(1,n+1,dtype=np.int32)*4
    v=np.minimum(256,gain+v) if audible else np.maximum(0,gain-v)
    gains[cursor:end]=v;expected[cursor:end]=b[cursor:end]+np.trunc(g[cursor:end]*v/256).astype(np.int32)
    if n:gain=int(v[-1])
    cursor=end
for e in events:
    end=int(e['sample']);fill(end);assert int(e['gain'])==gain,(e,gain)
    state=int(e['kind']) in (0,1)
    if state!=audible:transitions.append((end,state))
    audible=state
fill(len(g));assert np.max(abs(expected))<=127
muted=(gains==0)&(np.abs(b)>0)&(np.arange(len(g))>=32768)
assert np.array_equal(expected[muted],b[muted])
if a.require_mute:assert muted.sum()>1000,'no sustained true-silence guitar interval'
if a.require_recovery:assert any(on for _,on in transitions),'no recovery'
reference=expected.astype(float).repeat(2)
guitar_reference=g.astype(float).repeat(2);backing_reference=b.astype(float).repeat(2)
def match(start,length,label):
    start=max(0,start);end=min(len(reference),start+length)
    template=reference[start:end].copy();template-=template.mean()
    if len(template)<512 or np.dot(template,template)<1:return None
    # Translate each reference through its nearest independently observed
    # hardware/capture pair; also report the fixed-epoch residual separately.
    local_origin=int(epochs[int(np.argmin(np.abs(hardware_indices-start//2)))])
    guess=start+local_origin;lo=max(0,guess-64);search=actual[lo:guess+65+len(template)]
    if len(search)<len(template):return None
    dots=np.correlate(search,template,'valid');s=np.convolve(search,np.ones(len(template)),'valid');sq=np.convolve(search*search,np.ones(len(template)),'valid')
    scores=dots/np.sqrt(np.maximum(1,sq-s*s/len(template))*np.dot(template,template));best=int(np.argmax(scores));error=(lo+best-start-local_origin)*1000/32768;score=float(scores[best])
    assert score>.94,(label,'runtime_seconds',start/32768,'correlation',score,'error_ms',error);assert abs(error)<1,(label,'runtime_seconds',start/32768,'error_ms',error)
    result=dict(label=label,runtime_seconds=start/32768,correlation=score,error_ms=error,global_epoch_error_ms=(lo+best-start-origin)*1000/32768,capture_epoch_at_reference=local_origin)
    if label in ('guitar-on','backing-only'):
        # Include backing derivatives as nuisance terms for PWM/resampler
        # phase/curvature; otherwise filter error can look like negative guitar.
        back=backing_reference[start:end]
        slope=np.gradient(back);curvature=np.gradient(slope)
        design=np.column_stack((guitar_reference[start:end],back,np.ones(end-start),slope,curvature))
        coefficients=np.linalg.lstsq(design,actual[lo+best:lo+best+len(template)],rcond=None)[0]
        result['backing_scale']=float(coefficients[1])
        result['guitar_to_backing_scale']=float(coefficients[0]/coefficients[1]) if abs(coefficients[1])>1 else None
        if label=='backing-only':
            if not a.backing_capture:
                assert result['guitar_to_backing_scale'] is not None and abs(result['guitar_to_backing_scale'])<.03,('residual guitar',result)
            else:
                # Compare directly to a separate actual backing-only run. This
                # removes the common PWM/resampler response, rather than loosen
                # a failing unfiltered-reference coefficient tolerance.
                baseline_origin=int(be[np.argmin(abs(bi-start//2))]);center=start+baseline_origin
                target=actual[lo+best:lo+best+len(template)].copy();target-=target.mean()
                candidates=baseline[center-64:center+65+len(template)]
                dot=np.correlate(candidates,target,'valid');sums=np.convolve(candidates,np.ones(len(target)),'valid');squares=np.convolve(candidates*candidates,np.ones(len(target)),'valid')
                sc=dot/np.sqrt(np.maximum(1,squares-sums*sums/len(target))*np.dot(target,target));j=int(np.argmax(sc))
                base=candidates[j:j+len(target)].copy();base-=base.mean();scale=float(np.dot(base,target)/np.dot(base,base))
                residual=target-base*scale;lead=guitar_reference[start:end].copy();lead-=lead.mean()
                leak=float(np.dot(residual,lead)/max(1,np.dot(lead,lead))/abs(result['backing_scale']))
                result.update(backing_capture_correlation=float(sc[j]),backing_capture_scale=scale,residual_guitar_after_common_filter=leak)
                assert sc[j]>.999 and .98<scale<1.02,(label,'backing capture differs',result)
                assert abs(leak)<.01,('guitar remains after common-filter comparison',result)
    return result
checks=[]
for seconds in map(float,a.times.split(',')):
    r=match(round(seconds*32768)-256,8000,'sync-reference');assert r;checks.append(r)
# Sample steady ON/OFF windows throughout the full song, and actual fade edges.
for kind,mask in [('guitar-on',gains==256),('backing-only',gains==0)]:
    mask=mask.copy();mask[:32768+128]=False
    changes=np.diff(np.r_[False,mask,False].astype(int));starts=np.flatnonzero(changes==1);ends=np.flatnonzero(changes==-1)
    windows=[(int(x),int(y)) for x,y in zip(starts,ends) if y-x>1024 and np.dot(b[x:y].astype(float),b[x:y].astype(float))>0]
    for start,end in windows[::max(1,len(windows)//12)]:
        r=match((start+128)*2,min(4096,(end-start-256)*2),kind)
        if r:checks.append(r)
chosen_transitions=[]
for state in (False,True):
    group=[t for t in transitions if t[1]==state]
    chosen_transitions+=group[::max(1,len(group)//8)]
for sample,on in chosen_transitions:
    r=match(sample*2-256,2048,'fade-up' if on else 'fade-down')
    if r:checks.append(r)
if a.require_mute:assert any(c['label']=='backing-only' for c in checks),'no captured backing-only evidence'
if a.require_recovery:assert any(c['label']=='fade-up' for c in checks),'no captured recovery evidence'
assert not np.count_nonzero(np.abs(actual)>=32767),'captured clipping'
ended=[r for r in rows if r['state']=='2'];assert ended and all(r['tick']==ended[-1]['tick'] for r in ended[1:])
assert all(int(r['underruns'])==0 for r in rows),'underrun'
report=dict(format='16384Hz signed8 mono, two aligned ROM streams',capture_epoch_samples=origin,epoch_variation_samples=int(epochs.max()-epochs.min()),
            events=len(events),mute_transitions=sum(not on for _,on in transitions),recoveries=sum(on for _,on in transitions),
            exact_backing_only_source_samples=int(muted.sum()),fade_samples=64,fade_ms=64*1000/16384,
            independent_model_peak=int(abs(expected).max()),captured_peak=int(abs(actual).max()),clipped_samples=0,underruns=0,
            last_second_nonzero_samples=int(np.count_nonzero(actual[-32768:])),checks=checks)
Path(pre+'.analysis.json').write_text(json.dumps(report,indent=2)+'\n')
with wave.open(pre+'.wav','wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(32768);w.writeframes(Path(pre+'.raw').read_bytes())
print(json.dumps(report,indent=2))
