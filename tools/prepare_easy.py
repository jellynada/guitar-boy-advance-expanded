#!/usr/bin/env python3
"""One-command package inspection + explicit Easy adaptation (no ROM build)."""
import argparse
import json
from pathlib import Path
try:
    from .adapt_chart import adapt, header
    from .import_song import import_song
    from .import_chart import save_text
except ImportError:
    from adapt_chart import adapt, header
    from import_song import import_song
    from import_chart import save_text


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package',type=Path)
    parser.add_argument('--output-dir',type=Path,default=Path('imports/output/easy-runtime'))
    parser.add_argument('--chart')
    parser.add_argument('--audio',action='append')
    parser.add_argument('--offset-policy',choices=['add','ini','chart'])
    args=parser.parse_args()
    output=args.output_dir
    output.mkdir(parents=True,exist_ok=True)
    # Clear managed runtime assets before inspecting: failed import cannot build
    # the previous song under the new song's report.
    for name in ('imported_chart.hpp','adapted.json'):(output/name).unlink(missing_ok=True)
    if not import_song(args.package,output/'source',args.chart,args.audio,args.offset_policy):
        save_text(output/'adaptation_report.txt','INVALID: package import failed; read source report.txt.\n')
        return 1
    source=output/'source'/args.package.stem/'song.json'
    try:
        result=adapt(json.loads(source.read_text()),difficulty='Easy',instrument='five_fret_lead_guitar')
        save_text(output/'adapted.json',json.dumps(result,indent=2)+'\n')
        save_text(output/'imported_chart.hpp',header(result))
        lines=[f"Easy lead guitar: {result['note_count']}notes, all preserved.",
               f"Short releases {result['short_release_count']}; genuine sustains {result['genuine_sustain_count']}; threshold{result['sustain_threshold_ticks']}ticks.",
               'Mapping0=Left,1=A,2=B. Two-second pre-roll. Silent onset-only test.']+result['warnings']
        save_text(output/'adaptation_report.txt','\n'.join(lines)+'\n')
        print('\n'.join(lines))
        print(f'\nPrepared header: {output / "imported_chart.hpp"}')
        print('Build (Bash/WSL, Docker running):')
        print(f'bash scripts/build-docker.sh "IMPORTED_HEADER={output / "imported_chart.hpp"}"')
        return 0
    except (OSError,ValueError,KeyError,TypeError) as error:
        for name in ('imported_chart.hpp','adapted.json'):(output/name).unlink(missing_ok=True)
        save_text(output/'adaptation_report.txt',f'INVALID: {error}\n')
        print(f'INVALID: {error}');return 1


if __name__=='__main__':raise SystemExit(main())
