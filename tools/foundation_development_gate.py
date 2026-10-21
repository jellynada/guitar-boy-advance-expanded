"""Development integration only: require the exact documented audio limitation.

The strict audio job still fails and formal release remains blocked. Never use
this check as release approval or as an exception for a new runtime change.
"""
import argparse
import json
from pathlib import Path

RC2='9ccc460693fa7254527177330f32e56153720237'
HASH='9c4af95ff97eddd266dca3d7491ac9a5b1256f417684aae51b7c126443afafde'
CASES={19,4,22,0,12}
EXPECTED_FAILURES={(d,c)for d in range(3)for c in [4,22]}

def check(ordinary,statuses,source):
    for job in ['build','gameplay','digital','soak','focused-audio']:
        if statuses.get(job)!='success':raise ValueError('Required development check did not pass: '+job)
    if statuses.get('audio-output')!='failure':raise ValueError('Unexpected strict output job result; review required')
    if ordinary.get('source_commit')!=RC2 or ordinary.get('rom_sha256')!=HASH:
        raise ValueError('Stale or changed ROM in audio evidence')
    rows=ordinary.get('results',[])
    keys=[(r['difficulty'],r['case'])for r in rows]
    if len(keys)!=15 or set(keys)!={(d,c)for d in range(3)for c in CASES}:
        raise ValueError('Incomplete or duplicate ordinary matrix')
    if any(r['exit_code'] not in [0,1]for r in rows):
        raise ValueError('Crash or infrastructure error cannot be an accepted audio limitation')
    failures={(r['difficulty'],r['case'])for r in rows if r['exit_code']!=0}
    if failures!=EXPECTED_FAILURES or ordinary.get('passed')!=9 or ordinary.get('total')!=15 or ordinary.get('release_gate')!='blocked':
        raise ValueError('Ordinary output changed from the specifically reviewed 9/15 limitation')
    if not source.get('runtime_build_inputs_identical') or source.get('runtime_identity')!=RC2 or source.get('expected_rom_sha256')!=HASH:
        raise ValueError('Candidate source equivalence not established')
    if source.get('owner_foundation_accepted')is not True or source.get('pr_merge_approved')is not False:
        raise ValueError('Incorrect foundation/merge approval scope')
    return dict(development_integration_checks='passed',owner_foundation_accepted=True,
        pr_merge_approved=False,strict_audio_passed=False,strict_audio_passed_cases=9,
        strict_audio_total=15,release_promotion='blocked',release_approved=False,
        graphics_authorized=False,candidate_commit=source['candidate_commit'],candidate_tree=source['candidate_tree'])

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['ordinary','statuses','source','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();report=check(json.loads(a.ordinary.read_text()),json.loads(a.statuses.read_text()),json.loads(a.source.read_text()))
    a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
