"""Sample-exact source-time cut and derived chart recipe; no runtime decoder."""
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
try:
    from .audio_prepare import RATE, PRE_ROLL, GUARD
    from .adapt_chart import cycles, PRE_ROLL_US
    from .handheld_chart import adapt_handheld, recalculate, validate
except ImportError:
    from audio_prepare import RATE, PRE_ROLL, GUARD
    from adapt_chart import cycles, PRE_ROLL_US
    from handheld_chart import adapt_handheld, recalculate, validate

VERSION = 'gba-arcade-cut-v1'
FADE_SAMPLES = RATE * 75 // 1000  # 1228 samples, 74.951ms


def duration_samples(seconds):
    value = Fraction(str(seconds))
    if not 0 < value <= 1800: raise ValueError('Maximum duration must be >0 and <=1800 seconds')
    count = value * RATE
    if count.denominator != 1:
        raise ValueError('Maximum duration must fall on an exact 16384Hz sample boundary')
    return int(count)


def recipe(source_samples, max_duration=75, handheld=True):
    maximum = duration_samples(max_duration) if max_duration is not None else source_samples
    if type(source_samples) is not int or source_samples <= 0: raise ValueError('Invalid original audio length')
    return dict(version=VERSION, max_duration_seconds=str(max_duration) if max_duration is not None else None,
                original_source_samples=source_samples, source_samples=min(source_samples, maximum),
                cutoff_numerator=min(source_samples, maximum) * 1000000, cutoff_denominator=RATE,
                handheld=bool(handheld), fade_samples=min(FADE_SAMPLES, source_samples, maximum),
                pre_roll_samples=PRE_ROLL, tail_samples=0)


def transform_chart(native, policy):
    charts = native.get('charts', [native]); output = []; reports = []
    boundary = Fraction(policy['cutoff_numerator'], policy['cutoff_denominator'])
    # Existing clock intentionally represents the last consumed sample index,
    # not the boundary after it. Preserve that transport contract exactly.
    final_cycle = (PRE_ROLL + policy['source_samples'] - 1) * 1024
    for chart in charts:
        cut = copy.deepcopy(chart); kept = []; mapping = []
        for n in chart['notes']:
            item = copy.deepcopy(n); action = 'keep'
            if n['start_us'] >= boundary:
                mapping.append(dict(id=n['source_note_index'], source_tick=n['source_tick'], action='trim-remove', original=copy.deepcopy(n), prepared=None)); continue
            if n['genuine_sustain'] and (n['start_us'] + n['sustain_us'] > boundary or
                                       n['runtime_tick'] + cycles(n['sustain_us']) > final_cycle):
                duration = max(0, min(int(boundary - n['start_us']),
                                     (final_cycle - n['runtime_tick']) * 1000000 // 16777216))
                while duration and n['runtime_tick'] + cycles(duration) > final_cycle: duration -= 1
                item['sustain_us'] = duration; item['genuine_sustain'] = duration > 0
                item['end_us'] = item['start_us'] + duration; action = 'trim-hold'
            kept.append(item)
            mapping.append(dict(id=n['source_note_index'], source_tick=n['source_tick'], action=action, original=copy.deepcopy(n), prepared=copy.deepcopy(item)))
        cut['notes'] = kept; recalculate(cut)
        cut['title'] = 'ARCADE75 / HANDHELD' if policy['handheld'] and policy['max_duration_seconds'] == '75' else 'ARCADE CUT / ' + ('HANDHELD' if policy['handheld'] else 'NATIVE')
        trimmed_validation = validate(cut)
        if policy['handheld']: cut, adaptation = adapt_handheld(cut)
        else: adaptation = dict(changes=[], before=trimmed_validation, after=trimmed_validation)
        by_id = {n['source_note_index']: n for n in cut['notes']}
        for row in mapping:
            row['final'] = by_id.get(row['id'])
        reports.append(dict(difficulty=chart['difficulty'], original_heads=chart['note_count'],
                            original_sustains=chart['genuine_sustain_count'], trimmed_validation=trimmed_validation,
                            heads=cut['note_count'], sustains=cut['genuine_sustain_count'],
                            score_reference=cut['score_reference'], adaptation=adaptation, provenance=mapping))
        output.append(cut)
    result = copy.deepcopy(max(output, key=lambda x: x['note_count']))
    if 'charts' in native:
        result['difficulty'] = 'All'; result['charts'] = output
        result['notes'] = [n for c in output for n in c['notes']]
    result['preparation_recipe'] = policy
    return result, dict(version=VERSION, recipe=policy, charts=reports)


def fade_pcm(pcm, count):
    result = bytearray(pcm)
    if count <= 0: return bytes(result)
    if count == 1: result[-1] = 0; return bytes(result)
    # Identical integer envelope and signed nearest rounding for both roles.
    for i in range(count):
        value = result[len(result) - count + i]
        if value >= 128: value -= 256
        numerator = abs(value) * (count - 1 - i)
        q = (numerator + (count - 1) // 2) // (count - 1)
        result[len(result) - count + i] = (q if value >= 0 else -q) & 255
    return bytes(result)


def trim_audio(folder, audio, policy):
    folder = Path(folder); count = policy['source_samples']; reactive = audio['schema_version'] == 'gba-reactive-audio-v1'
    original = dict(audio); names = ['imported_audio.bin'] + (['imported_backing.bin'] if reactive else [])
    before_hashes = {}; source_hashes = {}; unfaded = {}
    for name in names:
        full = (folder / name).read_bytes(); before_hashes[name] = hashlib.sha256(full).hexdigest()
        source = full[PRE_ROLL:PRE_ROLL + count]; unfaded[name] = hashlib.sha256(source).hexdigest()
        pcm = fade_pcm(source, policy['fade_samples']); source_hashes[name] = hashlib.sha256(pcm).hexdigest()
        blob = bytes(PRE_ROLL) + pcm + bytes(GUARD); blob += bytes((-len(blob)) % 16)
        (folder / name).write_bytes(blob)
    size = (folder / names[0]).stat().st_size
    audio.update(arcade_cut=policy, original_source_samples=original['source_samples'],
                 original_stream_sha256=before_hashes, unfaded_cut_sha256=unfaded, cut_pcm_sha256=source_hashes,
                 source_samples=count, source_duration_seconds=count / RATE, tail_samples=0,
                 playback_samples=PRE_ROLL + count, byte_size=size,
                 pcm_sha256=hashlib.sha256((folder / names[0]).read_bytes()).hexdigest(),
                 origin='Sample zero unchanged; source-time cutoff excludes count-in; no playback tail; 75ms integer end fade; safety guard not played')
    if reactive:
        audio.update(total_byte_size=size * 2, backing_sha256=hashlib.sha256((folder / names[1]).read_bytes()).hexdigest())
    else: audio['source_pcm_sha256'] = source_hashes[names[0]]
    (folder / 'audio_report.txt').write_text(json.dumps(dict(recipe=policy, source_samples=count, playback_samples=audio['playback_samples'], byte_size=size,
        source_timeline='Decoder pre-skip retained; both streams sliced at identical sample indexes; 2s count-in unchanged; no tail'), indent=2) + '\n')
    return audio
