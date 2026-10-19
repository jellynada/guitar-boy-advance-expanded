#!/usr/bin/env python3
"""Build helper: public synthetic chart by default, explicit local header opt-in."""
import argparse
from pathlib import Path
from adapt_chart import adapt, header
from chart_importer import normalize

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--header',type=Path)
args=parser.parse_args()
if args.header:
    text=args.header.read_text(encoding='utf8')
else:
    root=Path(__file__).resolve().parents[1]
    song=normalize((root/'tests/fixtures/runtime/easy.chart').read_text(), 'Synthetic Easy Test')
    text=header(adapt(song,difficulty='Easy',instrument='five_fret_lead_guitar',synthetic=True))
args.output.parent.mkdir(parents=True,exist_ok=True)
if not args.output.exists() or args.output.read_text()!=text:
    args.output.write_text(text,encoding='utf8')
