#!/usr/bin/env python3
"""Run version-specific host-only observation against a verified ROM/ELF pair."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.verify_build import verify

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--rom',type=Path,required=True);p.add_argument('--elf',type=Path,required=True)
p.add_argument('--note-count',type=int,required=True);p.add_argument('--frames',type=int,default=16400)
p.add_argument('--scenario',default='reactive');p.add_argument('--prefix',type=Path,required=True)
p.add_argument('--emulator-prefix',default='[]',help='JSON command prefix')
p.add_argument('--diagnose-fifo-lateness',action='store_true',help='Experimental emulator correction; never a normal acceptance capture')
a=p.parse_args();root=Path(__file__).resolve().parents[1];a.rom=a.rom.resolve();a.elf=a.elf.resolve();a.prefix=a.prefix.resolve();a.prefix.parent.mkdir(parents=True,exist_ok=True)
print(json.dumps(verify(a.rom,a.elf,a.note_count)),flush=True)
pre=json.loads(a.emulator_prefix);tool=Path(os.environ['DEVKITARM'])/'bin/arm-none-eabi-nm'
symbols=subprocess.check_output([str(tool),str(a.elf)],text=True);syms={s[2]:s[0] for line in symbols.splitlines() if len(s:=line.split())==3}
Path(str(a.prefix)+'.symbols').write_text(symbols)
shared=str(a.prefix)+'.tap.so';runner=str(a.prefix)+'.runner'
subprocess.run(pre+['gcc','-std=gnu11','-O2','-Wall','-Wextra','-Werror','-fPIC','-shared',str(root/'tests/hardware_tap.c'),'-o',shared,'-lmgba','-ldl'],check=True)
subprocess.run(pre+['gcc','-O2','-Wall','-Wextra','-Werror',str(root/'tests/audio_emulator.c'),'-o',runner,'-lmgba'],check=True)
env={'LD_PRELOAD':shared,'GBA_HARDWARE_TAP':str(a.prefix),'GBA_TAP_MODE_ADDR':syms['gameMode'],'GBA_TAP_STATE_ADDR':syms['audioState'],'GBA_TAP_FILL_ADDR':syms['_ZL12fillPosition']}
if a.diagnose_fifo_lateness:env['GBA_TAP_CORRECT_FIFO_LATENESS']='1'
cmd=pre+['env']+[k+'='+v for k,v in env.items()]+[runner,str(a.rom),str(a.prefix)+'.symbols',str(a.note_count),str(a.frames),a.scenario,str(a.prefix)]
with Path(str(a.prefix)+'.log').open('w') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
print('Captured',a.prefix,flush=True)
