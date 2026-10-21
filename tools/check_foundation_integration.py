"""Verify the owner-approved foundation scope before a development-only PR.

This never merges, publishes or changes the game's build identity. It proves
that retaining RC2's runtime identity is legitimate for this exact source tree.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

RC2='9ccc460693fa7254527177330f32e56153720237'
BASE='56f6b7b243dfc710996336b99ac249806e666c85'
ACCEPTED_CODE='33b4d227e7e8142639486d1effeb67a81c15903e'
CLOSEOUT='81f104e5b206eea579f55bfe744e16d8004e9920'
ROM_HASH='9c4af95ff97eddd266dca3d7491ac9a5b1256f417684aae51b7c126443afafde'
BUILD_INPUTS=['source','include','graphics','charts','data','music','Makefile',
    'bin/chart_reader.cpp','tools/prepare_runtime.py','tools/adapt_chart.py',
    'tools/chart_importer.py','tools/build_audio.py','tools/audio_prepare.py',
    'tools/reactive_prepare.py','tools/validate_holds.py','tools/check_rom_size.py',
    'tools/verify_build.py','tools/write_build_identity.py','scripts/build-docker.sh',
    'scripts/toolchain-image.txt']
ALLOWED_ADDITIONS={'.github/workflows/m020-closeout.yml',
    'tools/check_foundation_integration.py','tools/foundation_development_gate.py',
    'tests/test_foundation_integration.py'}

def git(*args):
    return subprocess.check_output(['git',*args],text=True).strip()

def verify(output):
    for before,after in [(BASE,ACCEPTED_CODE),(ACCEPTED_CODE,CLOSEOUT),(CLOSEOUT,'HEAD')]:
        subprocess.run(['git','merge-base','--is-ancestor',before,after],check=True)
    changes=git('diff','--name-only',RC2,'HEAD','--',*BUILD_INPUTS).splitlines()
    if changes:raise ValueError('Runtime/build input differs from RC2: '+repr(changes))
    additions=git('diff','--name-only',CLOSEOUT,'HEAD').splitlines()
    if any(n not in ALLOWED_ADDITIONS and not n.startswith('docs/') and n!='README.md' for n in additions):
        raise ValueError('Unreviewed integration scope: '+repr(additions))
    if git('rev-parse','--is-shallow-repository')!='false':raise ValueError('Incomplete ancestry')
    parents=git('show','-s','--format=%P','HEAD').split()
    if os.environ.get('GITHUB_EVENT_NAME')=='pull_request' and (len(parents)!=2 or parents[0]!=BASE):
        raise ValueError('PR test merge has changed base; re-audit required')
    report=dict(schema='gba-foundation-integration-source-v1',candidate_commit=git('rev-parse','HEAD'),
        candidate_tree=git('rev-parse','HEAD^{tree}'),candidate_parents=parents,
        reviewed_develop=BASE,accepted_code=ACCEPTED_CODE,accepted_closeout=CLOSEOUT,
        runtime_identity=RC2,expected_rom_sha256=ROM_HASH,runtime_build_inputs_identical=True,
        integration_changes=additions,owner_foundation_accepted=True,pr_merge_approved=False,
        graphics_authorized=False,release_approved=False)
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    verify(p.parse_args().output)
