"""Bound stock PWM placement against timestamped FIFO bytes, not fitted waves."""
import argparse
import csv
import gzip
import json
from pathlib import Path
import numpy as np

def analyze(prefix):
    prefix=Path(prefix)
    def records(suffix):
        path=Path(str(prefix)+suffix)
        stream=path.open()if path.exists()else gzip.open(str(path)+'.gz','rt')
        with stream as f:return list(csv.DictReader(f))
    fifo=records('.m020-events.csv');pwm=records('.pwm-events.csv')
    assert len(fifo)>1000 and len(pwm)>1000
    times=np.array([int(r['cycle'])for r in fifo],dtype=np.int64)
    values=np.array([int(r['value'])for r in fifo],dtype=np.int64)*192
    pts=np.array([int(r['cycle'])for r in pwm],dtype=np.int64)
    actual=np.array([int(r['value'])for r in pwm],dtype=np.int64)
    late=np.array([int(r['late'])for r in fifo],dtype=np.int64)
    until=np.array([int(r['until'])for r in fifo],dtype=np.int64)
    expired=until<=0
    changes=np.diff(np.r_[False,expired,False].astype(int))
    runs=np.flatnonzero(changes==-1)-np.flatnonzero(changes==1)
    skipped=[]
    for row in fifo:
        u=int(row['until']);incoming=int(row['value']);previous=int(row['slot1'])
        # Independently apply the stock source's two-slot write range.
        slots_to_write=min(2,(u-1+512)>>9)
        if slots_to_write<=0 and incoming!=previous:
            next_pwm=int(np.searchsorted(pts,int(row['cycle'])+int(row['late'])))
            assert next_pwm<len(actual)
            skipped.append(dict(index=int(row['index']),incoming=incoming,previous=previous,
                next_pwm_value=int(actual[next_pwm]),retains_previous=bool(actual[next_pwm]==previous*192),
                emits_incoming=bool(actual[next_pwm]==incoming*192)))
    records=[]
    # Report both explicitly named slot boundaries; neither is waveform fitted.
    for name,boundary in [('slot-end',pts),('slot-start',pts-512)]:
        index=np.searchsorted(times,boundary,side='right')-1
        valid=(index>=2)&(index<len(times)-2)
        ix=index[valid];a=actual[valid]
        matches=np.column_stack([a==values[ix+offset]for offset in [-2,-1,0,1,2]])
        exact=matches[:,2];within_one=matches[:,1:4].any(axis=1)
        records.append(dict(boundary=name,pwm_samples=int(valid.sum()),
            exact_sample_matches=int(exact.sum()),
            matches_within_one_source_sample=int(within_one.sum()),
            unexplained_outside_one=int((~within_one).sum()),
            unexplained_outside_two=int((~matches.any(axis=1)).sum())))
    report=dict(diagnostic_only=True,acceptance_thresholds_unchanged=True,
        fifo_events=len(fifo),timer_period_min=int(np.diff(times).min()),
        timer_period_max=int(np.diff(times).max()),
        late_cycles_min=int(late.min()),late_cycles_max=int(late.max()),
        first_fifo_source_index=int(fifo[0]['index']),
        last_fifo_source_index=int(fifo[-1]['index']),
        output_slot_cycles=512,source_sample_cycles=1024,
        scheduled_fifo_to_pwm_deadline_cycles=sorted(set(map(int,until+late))),
        expired_pwm_deadlines=int(expired.sum()),
        maximum_consecutive_expired_deadlines=int(max(runs))if len(runs)else 0,
        changed_fifo_values_skipped_by_stock_slot_rule=len(skipped),
        next_pwm_retains_previous=sum(r['retains_previous']for r in skipped),
        next_pwm_emits_incoming=sum(r['emits_incoming']for r in skipped),
        first_skipped_examples=skipped[:3],
        models=records)
    Path(str(prefix)+'.event-analysis.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2));return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('prefix',type=Path)
    analyze(p.parse_args().prefix)
