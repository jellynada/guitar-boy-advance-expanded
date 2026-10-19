#!/usr/bin/env python3
"""Prepare an explicitly selected Easy lead-guitar chart; never rewrite music."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

try:
    from .import_chart import save_text
except ImportError:
    from import_chart import save_text

CLOCK_HZ = 16777216
FRAME_CYCLES = 280896
PRE_ROLL_US = 2_000_000
MAX_SONG_US = 7_200_000_000  # two hours, bounded separately from renderer coordinates
AHEAD_US, BEHIND_US = 1_000_000, 200_000
MAX_NOTES = 8192


def integer(value, label, minimum=0, maximum=(1 << 63) - 1):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f'{label} must be an integer in {minimum}..{maximum}.')
    return value


def cycles(us):
    integer(us, 'Runtime microseconds', maximum=MAX_SONG_US + PRE_ROLL_US)
    return (us * CLOCK_HZ + 500_000) // 1_000_000


def adapt(song, *, difficulty, instrument, synthetic=False):
    if song.get('schema_version') != 'gba-song-data-v1':
        raise ValueError('Expected Mission004 normalized gba-song-data-v1 JSON.')
    if song.get('timing', {}).get('unit') != 'microseconds':
        raise ValueError('Normalized timestamps must be in microseconds.')
    if difficulty != 'Easy' or instrument != 'five_fret_lead_guitar':
        raise ValueError('This adapter explicitly supports Easy five_fret_lead_guitar only.')
    selected = [t for t in song['tracks'] if t['difficulty'] == difficulty and t['instrument'] == instrument]
    if len(selected) != 1:
        raise ValueError('Exactly one Easy lead-guitar track must be selected.')
    notes = selected[0]['notes']
    if not notes or len(notes) > MAX_NOTES:
        raise ValueError('Selected chart must contain 1..8192 notes.')
    if any(e.get('type') == 'sysex' for e in selected[0]['special_events']):
        raise ValueError('Unapplied SysEx may change lanes; resolve it before adapting.')
    resolution = integer(song['resolution'], 'Resolution', 1, (1 << 32) - 1)
    # Explicit TEST policy: one third of a quarter note, independent of tempo.
    # Unlike a player sustain cutoff, this never changes raw duration/end time.
    cutoff = (resolution + 2) // 3
    transformed, warnings = [], []
    previous = previous_tick = -1
    seen = set()
    lane_ends = {}
    first_visible = 0
    max_visible = 0
    sustain_overlaps = 0
    for index, note in enumerate(notes):
        start = integer(note['start_us'], 'Note start', -PRE_ROLL_US, MAX_SONG_US)
        end = integer(note['end_us'], 'Note end', start, MAX_SONG_US)
        duration = integer(note['duration_us'], 'Note duration', maximum=MAX_SONG_US)
        duration_ticks = integer(note['duration_ticks'], 'Release ticks', maximum=(1 << 64) - 1)
        tick = integer(note['tick'], 'Note tick', maximum=(1 << 64) - 1)
        if tick < previous_tick or tick + duration_ticks >= 1 << 64:
            raise ValueError('Source ticks must be ordered and release ticks must fit unsigned64.')
        previous_tick = tick
        if start < previous or start + duration != end:
            raise ValueError('Notes must be ordered and start + duration must equal end.')
        previous = start
        lane = integer(note['lane'], 'Easy native lane', 0, 2)
        source_lane = integer(note['source_lane'], 'Source lane', 0, 2)
        if note['kind'] != 'fretted' or source_lane != lane:
            raise ValueError('Open/rewritten/unsupported lanes cannot be silently mapped.')
        if (start, lane) in seen:
            raise ValueError('Duplicate same-lane onset is not playable.')
        seen.add((start, lane))
        genuine = duration_ticks >= cutoff and duration > 0
        if lane in lane_ends and lane_ends[lane] > start:
            sustain_overlaps += 1
        if genuine:
            lane_ends[lane] = end
        transformed.append(dict(source_note_index=index, source_tick=note['tick'],
                                lane=lane, button=('Left', 'A', 'B')[lane],
                                start_us=start, end_us=end, native_duration_us=duration,
                                native_duration_ticks=duration_ticks, genuine_sustain=genuine,
                                runtime_tick=cycles(start + PRE_ROLL_US),
                                sustain_us=duration if genuine else 0))
        # Inclusive visibility bounds cover the renderer's complete time window.
        while start - transformed[first_visible]['start_us'] > AHEAD_US + BEHIND_US:
            first_visible += 1
        max_visible = max(max_visible, index - first_visible + 1)
    if max_visible > 32:
        raise ValueError(f'Chart needs {max_visible} visible sprites; hardware budget is32. No notes discarded.')
    if sustain_overlaps:
        warnings.append(f'{sustain_overlaps} native sustained same-lane overlaps retained; onset-only play does not require holding.')
    if selected[0]['modifiers'] or selected[0]['special_events']:
        warnings.append('HOPO/strum/tap/phrase/text markers remain in source JSON; this test judges every onset as a fresh press. No marker gameplay.')
    ini_cutoff = song.get('package', {}).get('song_ini', {}).get('sustain_cutoff_threshold')
    if ini_cutoff is not None:
        warnings.append(f'INI sustain_cutoff_threshold={ini_cutoff!r} is preserved in source. This explicit test policy uses {cutoff}ticks for classification, without altering durations.')
    warnings += ['Silence: no audio decoded, paired or started in Imported Easy Test.',
                 'Genuine sustain durations retained; no tails, held-note scoring or release judgment.',
                 'Only Easy native lanes0/1/2 map to Left/A/B; no collapsing or difficulty relabeling.']
    return dict(schema_version='gba-adapted-easy-v1', source_name=song['source_name'],
                title=song.get('metadata',{}).get('Name') or song['source_name'],
                source_sha256=song.get('source_sha256'), synthetic=synthetic,
                difficulty=difficulty, instrument=instrument, controls=['Left','A','B'],
                clock_hz=CLOCK_HZ, frame_cycles=FRAME_CYCLES, pre_roll_us=PRE_ROLL_US,
                offset_us=0, origin='mode start = chart audio zero minus two seconds; no audio playback',
                sustain_threshold_ticks=cutoff, sustain_policy='native duration >= ceil(PPQ/3); original lengths retained',
                note_count=len(notes), short_release_count=sum(not n['genuine_sustain'] for n in transformed),
                genuine_sustain_count=sum(n['genuine_sustain'] for n in transformed),
                maximum_visible_notes=max_visible, native_overlap_count=sustain_overlaps,
                notes=transformed, warnings=warnings)


def header(data):
    # Only runtime essentials go into ROM. Original+adapted JSON remain separate.
    lines=['// Generated Easy heads and genuine sustain durations; raw lengths remain in JSON.',
           '#pragma once', '#include "note.h"', '#include <cstdint>',
           f'inline constexpr uint32_t imported_note_count = {data["note_count"]};',
           f'inline constexpr bool imported_is_synthetic = {str(data["synthetic"]).lower()};',
           'inline constexpr char imported_title[] = '+json.dumps(''.join(c if 32<=ord(c)<=126 else '?' for c in str(data.get('title',data['source_name'])))[:96],ensure_ascii=True)+';',
           'inline constexpr uint32_t imported_ticks_per_frame = 280896;',
           'inline constexpr uint64_t imported_pre_roll_us = 2000000;',
           'inline constexpr Note imported_notes[] = {']
    lines += [f'    {{{n["runtime_tick"]}ULL, {n["lane"]}U, 0U}},' for n in data['notes']]
    lines += ['};', '// Genuine native sustain durations in microseconds, parallel to imported_notes.',
              'inline constexpr uint64_t imported_sustain_us[] = {']
    lines += [f'    {n["sustain_us"]}ULL,' for n in data['notes']]
    lines += ['};','']
    return '\n'.join(lines)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('song_json',type=Path)
    parser.add_argument('--difficulty',required=True,choices=['Easy'])
    parser.add_argument('--instrument',required=True,choices=['five_fret_lead_guitar'])
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--synthetic',action='store_true',help='Label only original synthetic fixtures, never real songs')
    args=parser.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    try:
        raw=args.song_json.read_bytes()
        result=adapt(json.loads(raw),difficulty=args.difficulty,instrument=args.instrument,synthetic=args.synthetic)
        result['normalized_input_sha256']=hashlib.sha256(raw).hexdigest()
        save_text(args.output_dir/'adapted.json',json.dumps(result,indent=2)+'\n')
        save_text(args.output_dir/'imported_chart.hpp',header(result))
        counts=Counter(n['lane'] for n in result['notes'])
        lines=[f'Easy lead-guitar adaptation: {result["source_name"]}',
               f'Notes preserved: {result["note_count"]}; native lane counts: {dict(sorted(counts.items()))}',
               'Explicit mapping: 0=Left,1=A,2=B. No notes removed or lanes renumbered.',
               f'Short releases: {result["short_release_count"]}; genuine sustains: {result["genuine_sustain_count"]}',
               f'Threshold: {result["sustain_threshold_ticks"]} MIDI/chart ticks (ceil(PPQ/3)). All raw lengths remain in adapted JSON.',
               f'Maximum visible notes: {result["maximum_visible_notes"]}/32; native overlaps: {result["native_overlap_count"]}',
               'Runtime: exact CPU-cycle units, 2-second pre-roll, zero extra offset.',
               'Mode: three-lane onset-only silent test. No audio synchronization claim.']
        lines += ['WARNING: '+w for w in result['warnings']]
        save_text(args.output_dir/'adaptation_report.txt','\n'.join(lines)+'\n')
        print('\n'.join(lines));return 0
    except (OSError,ValueError,KeyError,TypeError) as error:
        for name in ('adapted.json','imported_chart.hpp'):
            (args.output_dir/name).unlink(missing_ok=True)
        message=f'INVALID: {error}'
        save_text(args.output_dir/'adaptation_report.txt',message+'\n')
        print(message);return 1


if __name__=='__main__':raise SystemExit(main())
