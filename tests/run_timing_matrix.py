#!/usr/bin/env python3
"""Developer-only controlled builds; never substitutes audio in a playable release."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile
import io
import shutil
import numpy as np

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source-ref',default='233112a072e5a0e90e5a766207761474130f75a6')
p.add_argument('--output',type=Path,required=True)
p.add_argument('--private-header',type=Path)
p.add_argument('--private-audio',type=Path)
p.add_argument('--emulator-prefix',default='[]',help='JSON command prefix, e.g. ["docker","exec","mission001-mgba"]')
p.add_argument('--resume',action='store_true')
p.add_argument('--frames',type=int,default=1800)
p.add_argument('--cases',default='synthetic,silent,cream,cream-tones,long-tones,long-zeros,no-tails,original')
a=p.parse_args();repo=Path(__file__).resolve().parents[1];out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
work=out/'guitar-boy-advance-expanded'
if work.exists() and not a.resume:raise SystemExit('Use a fresh output folder or --resume; existing source export is preserved.')
work.mkdir(exist_ok=True);archive=subprocess.check_output(['git','archive',a.source_ref],cwd=repo)
with tarfile.open(fileobj=io.BytesIO(archive)) as t:t.extractall(work,filter='data')
source_sha=subprocess.check_output(['git','rev-parse',a.source_ref],cwd=repo,text=True).strip()
env=os.environ.copy();devkit=Path(env['DEVKITARM']);env['PATH']=str(devkit/'bin')+':'+str(Path(env['DEVKITPRO'])/'tools/bin')+':'+env['PATH']
prefix=json.loads(a.emulator_prefix)
# Host tools are compiled from current QA source; game source is the pinned ref.
subprocess.run(prefix+['gcc','-O2','-Wall','-Wextra','-Werror',str(repo/'tests/timing_emulator.c'),'-o',str(out/'timing'),'-lmgba'],check=True)
subprocess.run(prefix+['gcc','-std=gnu11','-O2','-Wall','-Wextra','-Werror','-fPIC','-shared',str(repo/'tests/hardware_tap.c'),'-o',str(out/'tap.so'),'-lmgba','-ldl'],check=True)
synth=out/'synthetic.hpp';subprocess.run(['python3','tools/prepare_runtime.py','--output',str(synth)],cwd=work,check=True)
private=a.private_header.resolve() if a.private_header else None;audio=a.private_audio.resolve() if a.private_audio else None
samples=json.loads((audio/'audio.json').read_text())['source_samples'] if audio else 4378983
RATE=16384;PRE=32768;TAIL=8192;GUARD=16384;play=PRE+samples+TAIL;size=(play+GUARD+15)//16*16
fixtures={}
for name,zero in [('tones',False),('zeros',True)]:
 dest=out/('fixture-'+name);dest.mkdir(exist_ok=True);i=np.arange(samples,dtype=np.float64)
 g=np.zeros(size,dtype=np.int8);b=np.zeros(size,dtype=np.int8)
 if not zero:
  g[PRE:PRE+samples]=np.rint(24*np.sin(2*np.pi*440*i/RATE)).astype(np.int8)
  b[PRE:PRE+samples]=np.rint(12*np.sin(2*np.pi*220*i/RATE)).astype(np.int8)
 fixtures[name]=(dest,g.tobytes(),b.tobytes())
def prepare(name,header):
 dest,g,b=fixtures[name];(dest/'imported_audio.bin').write_bytes(g);(dest/'imported_backing.bin').write_bytes(b)
 manifest=dict(schema_version='gba-reactive-audio-v1',synthetic=True,sample_rate=RATE,channels=1,format='signed8_pcm',source_samples=samples,playback_samples=play,pre_roll_samples=PRE,tail_samples=TAIL,guard_samples=GUARD,byte_size=size,total_byte_size=size*2,pcm_sha256=hashlib.sha256(g).hexdigest(),backing_sha256=hashlib.sha256(b).hexdigest(),prepared_chart_sha256=hashlib.sha256(header.read_bytes()).hexdigest(),diagnostic_only=True)
 (dest/'audio.json').write_text(json.dumps(manifest,indent=2)+'\n');return dest
original_main=(work/'source/main.cpp').read_bytes();results=json.loads((out/'matrix.json').read_text()) if a.resume and (out/'matrix.json').exists() else {}
for case in a.cases.split(','):
 if case in results:continue
 if case in ('cream','cream-tones','no-tails') and not(private and audio):raise SystemExit('Real-chart matrix requires --private-header and --private-audio.')
 case_out=out/case;case_out.mkdir(exist_ok=True);args=[];header=private if case in ('cream','cream-tones','no-tails') else synth
 (work/'source/main.cpp').write_bytes(original_main)
 if case=='no-tails':
  old=b'if(gameMode==2)SustainDisplay::draw(importedNowCycles);';assert old in original_main
  (work/'source/main.cpp').write_bytes(original_main.replace(old,b'/* Diagnostic only: sustain draw omitted, judgment/holds preserved. */'))
 if case not in ('synthetic','original'):args+=['IMPORTED_HEADER='+str(header)]
 if case in ('cream','no-tails'):args+=['AUDIO_DIR='+str(audio)]
 elif case in ('cream-tones','long-tones','long-zeros'):args+=['AUDIO_DIR='+str(prepare('zeros' if case=='long-zeros' else 'tones',header))]
 with (case_out/'build.log').open('w') as log:subprocess.run(['make','-j2']+args,cwd=work,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 for suffix in ('gba','elf'):shutil.copyfile(work/('guitar-boy-advance-expanded.'+suffix),case_out/('game.'+suffix))
 sym=subprocess.check_output([str(devkit/'bin/arm-none-eabi-nm'),str(case_out/'game.elf')],text=True);(case_out/'symbols').write_text(sym)
 syms={s[2]:s[0] for line in sym.splitlines() if len(s:=line.split())==3}
 count=int(re.search(r'imported_note_count = (\d+)',(work/'build/imported_chart.hpp').read_text())[1])
 tap={'GBA_HARDWARE_TAP':str(case_out/'run'),'GBA_TAP_MODE_ADDR':syms['gameMode'],'GBA_TAP_STATE_ADDR':syms['audioState'],'GBA_TAP_FILL_ADDR':syms.get('_ZL12fillPosition','00000000'),'GBA_TAP_NO_PCM':'1','GBA_TAP_GRAPHICS_MODE':'1' if case=='original' else '2','LD_PRELOAD':str(out/'tap.so')}
 command=prefix+['env']+[k+'='+v for k,v in tap.items()]+[str(out/'timing'),str(case_out/'game.gba'),str(case_out/'symbols'),str(count),str(a.frames),'original' if case=='original' else 'imported',str(case_out/'run'),'1']
 with (case_out/'run.log').open('w') as log:subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
 result=json.loads((case_out/'run.timing.json').read_text());result.update(json.loads((case_out/'run.hardware.json').read_text()));result.update(source=source_sha,rom_sha256=hashlib.sha256((case_out/'game.gba').read_bytes()).hexdigest(),rom_bytes=(case_out/'game.gba').stat().st_size)
 results[case]=result;(out/'matrix.json').write_text(json.dumps(results,indent=2)+'\n');print(case,{k:result[k] for k in ['rom_bytes','defect_frames','worst_displaced_pixels','late_affine_writes','refill_max','foreground_max','peak_tails']},flush=True)
