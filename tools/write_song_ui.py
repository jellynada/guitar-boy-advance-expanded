#!/usr/bin/env python3
"""Bounded display metadata; never prepares or changes a chart or audio stream."""
import argparse,json
from pathlib import Path

def header(profile,metadata=None):
 if profile=='public-demo':
  if metadata is not None:raise ValueError('Public demo metadata is fixed original content')
  identifier,title,artist='copper-circuit','Synth Demo','Original composition'
 elif profile in ('song-private','cream-private'):
  if metadata is None:identifier,title,artist='imported-package',None,''
  else:
   d=metadata.get('metadata',{});identifier='imported-package';title=d.get('Name');artist=d.get('Artist','')
   if not isinstance(title,str) or not title:raise ValueError('Missing verified package title')
 else:identifier,title,artist='synthetic-easy-fixture','Synth Demo 2','Original test fixture'
 def string(s):
  if s is None:return 'nullptr'
  if not isinstance(s,str):raise ValueError('Invalid metadata string')
  s=''.join(c if 32<=ord(c)<=126 else '?'for c in s)[:63]
  return json.dumps(s,ensure_ascii=True)
 return '// Generated display-only metadata. Stable source names remain unchanged.\n#pragma once\n'+''.join(f'#define {k} {string(v)}\n'for k,v in [('UI_SONG_ID',identifier),('UI_SONG_TITLE',title),('UI_SONG_ARTIST',artist)])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--profile',required=True);p.add_argument('--metadata',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 content=header(a.profile,json.loads(a.metadata.read_text())if a.metadata else None);a.output.parent.mkdir(parents=True,exist_ok=True)
 if not a.output.exists()or a.output.read_text()!=content:a.output.write_text(content)
