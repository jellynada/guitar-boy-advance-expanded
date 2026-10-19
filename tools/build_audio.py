#!/usr/bin/env python3
"""Build-time deterministic public audio or validated explicit prepared private assets."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import tempfile
from audio_prepare import RATE,PRE_ROLL,TAIL,GUARD,MAX_ROM_AUDIO
from chart_importer import normalize
from reactive_prepare import synthetic_reactive


def write_if_changed(path,data):
    if not path.exists() or path.read_bytes()!=data:path.write_bytes(data)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--audio-dir',type=Path)
    parser.add_argument('--private-chart',action='store_true')
    args=parser.parse_args();out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
    if args.audio_dir and str(args.audio_dir)!='none':
        manifest=json.loads((args.audio_dir/'audio.json').read_text())
        if manifest.get('schema_version') not in ('gba-audio-v1','gba-reactive-audio-v1'):raise ValueError('Unsupported prepared audio schema.')
        reactive=manifest['schema_version']=='gba-reactive-audio-v1'
        blob=(args.audio_dir/'imported_audio.bin').read_bytes()
        for key in ('sample_rate','channels','pre_roll_samples','tail_samples','guard_samples','byte_size','playback_samples','source_samples'):
            if type(manifest.get(key)) is not int or manifest[key]<0:raise ValueError(f'Invalid integer audio metadata:{key}')
        if not 0<manifest['source_samples']<=1800*RATE:raise ValueError('Invalid source sample count.')
        if manifest['sample_rate']!=RATE or manifest['channels']!=1 or manifest['format']!='signed8_pcm':raise ValueError('Unsupported prepared audio format.')
        if manifest['pre_roll_samples']!=PRE_ROLL or manifest['tail_samples']!=TAIL or manifest['guard_samples']!=GUARD:raise ValueError('Prepared timing/padding mismatch.')
        if len(blob)>MAX_ROM_AUDIO or len(blob)!=manifest['byte_size'] or len(blob)%16 or hashlib.sha256(blob).hexdigest()!=manifest['pcm_sha256']:raise ValueError('Prepared PCM size/hash/alignment mismatch; prepare again.')
        if manifest['playback_samples']!=PRE_ROLL+manifest['source_samples']+TAIL or len(blob)<manifest['playback_samples']+GUARD:raise ValueError('Prepared audio sample counts disagree.')
        if any(blob[:PRE_ROLL]) or any(blob[PRE_ROLL+manifest['source_samples']:]):raise ValueError('Pre-roll/tail/guard must be signed8 silence.')
        chart=(out/'imported_chart.hpp').read_bytes()
        if manifest.get('prepared_chart_sha256') and hashlib.sha256(chart).hexdigest()!=manifest['prepared_chart_sha256']:raise ValueError('Audio was prepared for a different chart header.')
        ticks=[int(t) for t in re.findall(rb'\{(\d+)ULL,',chart)]
        if not ticks or max(ticks)+1426063 > (manifest['playback_samples']-1)*1024:raise ValueError('Audio ends before chart final late window.')
        backing=(args.audio_dir/'imported_backing.bin').read_bytes() if reactive else bytes(16)
        if reactive:
            if len(backing)!=len(blob) or len(blob)*2>MAX_ROM_AUDIO or hashlib.sha256(backing).hexdigest()!=manifest.get('backing_sha256') or manifest.get('total_byte_size')!=len(blob)*2:raise ValueError('Reactive backing size/hash/budget mismatch.')
            if any(backing[:PRE_ROLL]) or any(backing[PRE_ROLL+manifest['source_samples']:]):raise ValueError('Backing padding must be silence.')
            signed=lambda x:x if x<128 else x-256
            if any(abs(signed(x))+abs(signed(y))>127 for x,y in zip(blob,backing)):raise ValueError('Unsafe reactive mix headroom.')
        enabled=True
    elif args.private_chart or args.audio_dir:
        blob=backing=bytes(16);manifest={'source_samples':0,'playback_samples':0};enabled=reactive=False
    else:
        root=Path(__file__).resolve().parents[1]
        song=normalize((root/'tests/fixtures/runtime/easy.chart').read_text(),'Synthetic Easy Test')
        with tempfile.TemporaryDirectory() as tmp:
            manifest=synthetic_reactive(song,tmp);blob=(Path(tmp)/'imported_audio.bin').read_bytes();backing=(Path(tmp)/'imported_backing.bin').read_bytes()
        enabled=reactive=True
    text=f'''// Generated, validated audio metadata. No runtime decoder.
#pragma once
#include <cstdint>
inline constexpr bool imported_audio_reactive = {str(reactive).lower()};
inline constexpr bool imported_audio_enabled = {str(enabled).lower()};
inline constexpr uint32_t imported_audio_rate = {RATE};
inline constexpr uint32_t imported_audio_source_samples = {manifest['source_samples']};
inline constexpr uint32_t imported_audio_playback_samples = {manifest['playback_samples']};
'''
    write_if_changed(out/'imported_audio.bin',blob)
    write_if_changed(out/'imported_backing.bin',backing)
    write_if_changed(out/'imported_audio.hpp',text.encode())


if __name__=='__main__':
    try:main()
    except (OSError,ValueError,KeyError) as error:raise SystemExit('Audio build validation failed: '+str(error))
