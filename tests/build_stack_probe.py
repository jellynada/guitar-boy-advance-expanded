#!/usr/bin/env python3
"""Generate read-only gameplay regression plus unused-stack canary instrumentation.
Usage: python3 tests/build_stack_probe.py /tmp/resource.c
Compile output against libmgba and run with audio_emulator.c's normal arguments.
Only unused stack memory is written; no input/judgment/audio state is changed.
"""
from pathlib import Path
import sys
root=Path(__file__).resolve().parent
s=(root/'audio_emulator.c').read_text()
s=s.replace('int main(int argc,char** argv){',(root/'stack_probe.h').read_text()+'\nint main(int argc,char** argv){')
s=s.replace('assert(c->busRead32(c,modeaddr)==0);screenshot','assert(c->busRead32(c,modeaddr)==0);initProbe(c,syms);screenshot')
s=s.replace('c->deinit(c);mLogSetDefaultLogger','endProbe(c);c->deinit(c);mLogSetDefaultLogger')
Path(sys.argv[1]).write_text(s)
