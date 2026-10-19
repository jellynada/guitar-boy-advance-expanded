#!/usr/bin/env python3
"""Inspect package, select Easy and explicit matching audio stems; prepare one ROM mix."""
import argparse
import json
from pathlib import Path
import tempfile
try:
    from .audio_prepare import convert_files,RATE
    from .adapt_chart import adapt,header
    from .import_chart import save_text
    from .import_song import import_song
    from .song_package import Package
except ImportError:
    from audio_prepare import convert_files,RATE
    from adapt_chart import adapt,header
    from import_chart import save_text
    from import_song import import_song
    from song_package import Package


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package',type=Path)
    selection=parser.add_mutually_exclusive_group(required=True)
    selection.add_argument('--stem',action='append',help='Explicit unique role: song, guitar, rhythm; repeat. Preview prohibited.')
    selection.add_argument('--audio',action='append',help='Explicit relative audio file inside package; repeat to resolve ambiguity.')
    parser.add_argument('--chart')
    parser.add_argument('--offset-policy',choices=['add','ini','chart'])
    parser.add_argument('--output-dir',type=Path,default=Path('imports/output/song-runtime'))
    args=parser.parse_args();out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
    for path in (out/'imported_chart.hpp',out/'adapted.json',out/'audio/audio.json',out/'audio/imported_audio.bin',out/'audio/audio_report.txt',out/'audio_error.txt',out/'adaptation_report.txt'):path.unlink(missing_ok=True)
    try:
        if not import_song(args.package,out/'source',args.chart,args.audio,args.offset_policy):raise ValueError('Package invalid; read source report.')
        source=json.loads((out/'source'/args.package.stem/'song.json').read_text())
        adapted=adapt(source,difficulty='Easy',instrument='five_fret_lead_guitar')
        chosen=[]
        if args.stem:
            if len(set(args.stem))!=len(args.stem) or 'preview' in args.stem:raise ValueError('Select unique gameplay stems; preview is not gameplay audio.')
            for role in args.stem:
                matches=[s for s in source['package']['audio_streams'] if s['role']==role]
                if len(matches)!=1:raise ValueError(f'Stem {role!r}: expected exactly one file, found{len(matches)}. Use --audio to select exact package paths.')
                chosen.append(matches[0]['file'])
        else:
            if len(set(args.audio))!=len(args.audio):raise ValueError('Duplicate audio selection.')
            for name in args.audio:
                stream=next(s for s in source['package']['audio_streams'] if s['file']==name)
                if stream['role']=='preview':raise ValueError('Preview cannot replace gameplay audio.')
                chosen.append(name)
        with Package(args.package) as package,tempfile.TemporaryDirectory(prefix='gba-stems-') as temp:
            paths=[]
            for i,name in enumerate(chosen):
                path=Path(temp)/f'{i}-{Path(name).name}'
                path.write_bytes(package.read(name,128*1024*1024));paths.append(path)
            audio=convert_files(paths,out/'audio')
        if max(n['start_us'] for n in adapted['notes']) > audio['source_samples']*1000000//RATE:
            raise ValueError('Selected audio ends before the final note onset; verify matching stems/offsets.')
        import hashlib
        audio['prepared_chart_sha256']=hashlib.sha256(header(adapted).encode()).hexdigest()
        audio['chart_note_count']=adapted['note_count']
        audio['chart_source_sha256']=source.get('source_sha256')
        audio['selected_package_files']=chosen
        (out/'audio/audio.json').write_text(json.dumps(audio,indent=2)+'\n')
        save_text(out/'imported_chart.hpp',header(adapted))
        save_text(out/'adapted.json',json.dumps(adapted,indent=2)+'\n')
        save_text(out/'adaptation_report.txt',f"{adapted['note_count']} Easy notes preserved, Left/A/B, pre-roll2s. Audio stems explicitly selected:{chosen}.\n"+'\n'.join(w for w in adapted['warnings'] if not w.startswith('Silence:'))+'\n')
        print((out/'audio/audio_report.txt').read_text())
        print('Build in Ubuntu/WSL:')
        print(f'bash scripts/build-docker.sh "IMPORTED_HEADER={out}/imported_chart.hpp" "AUDIO_DIR={out}/audio"')
        return 0
    except (OSError,ValueError,KeyError,TypeError,__import__('subprocess').SubprocessError) as error:
        for path in (out/'imported_chart.hpp',out/'adapted.json',out/'audio/audio.json',out/'audio/imported_audio.bin'):path.unlink(missing_ok=True)
        save_text(out/'audio_error.txt',str(error)+'\n');save_text(out/'adaptation_report.txt','INVALID: audio/chart preparation failed; see audio_error.txt.\n');print(f'PREPARATION FAILED: {error}');return 1


if __name__=='__main__':raise SystemExit(main())
