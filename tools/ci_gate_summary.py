"""Bounded public-only CI diagnostics when signed-out Actions logs are unavailable.

This reports evidence after a gate; it never changes that gate's exit status.
Never pass a private build directory to this public workflow helper.
"""
import argparse
import json
import os
from pathlib import Path


def emit(text):
    text=text.replace('%','%25').replace('\r','%0D').replace('\n','%0A')
    print('::notice title=Certification evidence::'+text)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('directories',nargs='+',type=Path);a=p.parse_args();lines=[]
    for directory in a.directories:
        if not directory.exists():lines.append(str(directory)+': no evidence; stage did not complete');continue
        for name in ['verification.json','digital-verification.json','audio-output.json','FAILED.json']:
            q=directory/name
            if q.exists():
                value=json.loads(q.read_text());line=str(q)+': '+json.dumps(value,separators=(',',':'))[:1700];lines.append(line)
        for q in sorted(directory.glob('*.log')):
            text=q.read_text(errors='replace')
            if any(x in text for x in ['Assertion','Traceback','error:','failed:']):lines.append(str(q)+': '+' | '.join(text.splitlines()[-3:])[:1000])
    for line in lines[:20]:emit(line)
    if os.getenv('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'],'a')as f:f.write('### Actual gate evidence\n\n```text\n'+'\n'.join(lines[:20])+'\n```\n')
