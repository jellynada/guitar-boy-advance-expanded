"""Inherited scoring/sustain/fault observers on the unchanged 25-head fixture.
The forged early-EOF inconsistency scenario belongs to this non-cut fixture;
finite-cut songs intentionally resolve pending heads at declared EOF.
"""
import argparse,subprocess,sys,json,os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from build_ui_probes import generate
MODES=['perfect','good','miss','scoring','reactive','wrong','sustain-perfect','sustain-release','fault_dma','fault_sound','fault_irq','fault_underrun','fault_timer','inconsistent','returnmenu','returnselect','replaystart']
def run(rom,symbols,output,probe=None):
 r=Path(__file__).resolve().parents[1];output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False)
 if not probe:
  p=generate(r,output/'probes');probe=output/'audio';subprocess.run(['gcc','-O2','-I'+str(r/'tests'),str(p/'audio.c'),'-o',str(probe),'-lmgba'],check=True)
 def job(mode):
  prefix=output/mode
  with Path(str(prefix)+'.log').open('w')as f:rc=subprocess.run(list(map(str,[probe,rom,symbols,25,1200 if mode.startswith('fault')or mode=='inconsistent'else 1900,mode,prefix])),stdout=f,stderr=subprocess.STDOUT).returncode
  return dict(mode=mode,exit_code=rc)
 with ThreadPoolExecutor(max_workers=3)as pool:results=list(pool.map(job,MODES))
 (output/'verification.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2));assert all(x['exit_code']==0 for x in results),'Inherited fixture observer failed'
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--symbols',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--probe',type=Path);a=p.parse_args();run(a.rom.resolve(),a.symbols.resolve(),a.output,a.probe)
