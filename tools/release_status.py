"""Report independent gates; never infer owner acceptance from a green build."""
import argparse
import json
from pathlib import Path


def status(build, gameplay, digital, output):
    identities=[build.get('source_commit'),gameplay.get('source_commit'),digital.get('source_commit'),output.get('source_commit')]
    hashes=[build.get('rom_sha256'),gameplay.get('rom_sha256'),digital.get('rom_sha256'),output.get('rom_sha256')]
    identity_ok=bool(identities[0] and hashes[0])and len(set(identities))==1 and len(set(hashes))==1
    return dict(source_commit=identities[0],rom_sha256=hashes[0],
                build_succeeded=identity_ok and build.get('status')=='success',
                gameplay_passed=identity_ok and gameplay.get('result')=='passed',
                digital_passed=identity_ok and digital.get('passed')is True,
                audio_output_passed=identity_ok and output.get('release_gate')=='passed'and output.get('passed')==15 and output.get('total')==15,
                owner_accepted=False,release_approved=False,
                promotion='blocked; mandatory technical gates and separate owner approval required')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['build','gameplay','digital','output']:p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--write',type=Path,required=True);p.add_argument('--require-release',action='store_true');a=p.parse_args()
    r=status(*[json.loads(getattr(a,n).read_text())for n in ['build','gameplay','digital','output']]);a.write.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
    if a.require_release:raise SystemExit(0 if r['release_approved']else 1)
