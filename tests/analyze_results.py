#!/usr/bin/env python3
"""Check the actual GBA results tilemap against the emulator's scoring snapshot."""
import argparse,re
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prefix',type=Path,required=True);p.add_argument('--log',type=Path,required=True);a=p.parse_args()
text=Path(str(a.prefix)+'.screen.txt').read_text();log=a.log.read_text()
m=re.search(r'SCORE: score(\d+) combo(\d+) maximum(\d+) highest(\d+) accuracy(\d+) FC(\d+) AP(\d+) session(\d+)',log);assert m,'missing score snapshot'
score,combo,maximum,highest,accuracy,fc,ap,state=map(int,m.groups())
if state==1:
 assert text.splitlines()[0].strip()=='RESULTS'
else:
 assert ('AUDIO ERROR' if state==2 else 'DATA ERROR') in text
 assert 'RESULTS' not in text and 'SONG COMPLETE' not in text and 'FULL COMBO' not in text
for label,value in [('SCORE' if state==1 else 'PARTIAL SCORE',score),('MAX COMBO',maximum),('HIGHEST X',highest)]:
 assert re.search(r'^\s*'+label+r'\s+'+str(value)+r'\s*$',text,re.M),(label,value,text)
assert f'{accuracy//100}.{accuracy%100:02d}%' in text
stats=re.search(r'Perfect(\d+) Good(\d+) Miss(\d+) Wrong(\d+)',log);assert stats
for label,value in zip(['PERFECT','GOOD','MISS','WRONG INPUT'],stats.groups()):assert re.search(r'^\s*'+label+r'\s+'+value+r'\s*$',text,re.M)
assert ('ALL PERFECT' in text)==bool(ap) and ('FULL COMBO' in text)==bool(fc)
assert 'A / START: REPLAY' in text and 'B / SELECT: MODE SELECT' in text
print('PASS: actual results tilemap matches score, accuracy, judgments, maximum combo, multiplier, eligibility, status and controls')
