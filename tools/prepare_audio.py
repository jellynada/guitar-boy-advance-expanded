#!/usr/bin/env python3
"""Convert explicitly selected authorized files into GBA mono PCM."""
import argparse
from pathlib import Path
from audio_prepare import convert_files

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--file',type=Path,action='append',required=True)
parser.add_argument('--output-dir',type=Path,required=True)
args=parser.parse_args()
try:
    result=convert_files(args.file,args.output_dir)
    print((args.output_dir/'audio_report.txt').read_text())
except (OSError,ValueError,TimeoutError,__import__('subprocess').SubprocessError) as error:
    for name in ('imported_audio.bin','audio.json'):(args.output_dir/name).unlink(missing_ok=True)
    parser.exit(1,f'Audio preparation failed: {error}\n')
