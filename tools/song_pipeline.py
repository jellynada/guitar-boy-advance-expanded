#!/usr/bin/env python3
"""Versioned, private-by-default package preparation; no GBA runtime changes."""
import argparse
import configparser
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
import zipfile

try:
    from .adapt_chart import adapt, header
    from .audio_prepare import convert_files, RATE
    from .reactive_prepare import convert_reactive
    from .song_package import Package, inspect
    from .release_common import digest, file_hash, tree_digest
except ImportError:
    from adapt_chart import adapt, header
    from audio_prepare import convert_files, RATE
    from reactive_prepare import convert_reactive
    from song_package import Package, inspect
    from release_common import digest, file_hash, tree_digest

SCHEMA = 'gba-prepared-song-v1'
CONTROLS = ['LEFT', 'B', 'A']
FILES = {'normalized-song.json', 'adapted.json', 'imported_chart.hpp',
         'audio/audio.json', 'audio/imported_audio.bin', 'audio/imported_backing.bin',
         'audio/audio_report.txt', 'validation-report.json', 'validation-report.txt'}
MANIFEST = 'song-manifest.json'


def save(path, data):
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + '\n')


def runtime_adaptation(song):
    # Do not change the existing adapter or its Cream/public regression fixtures.
    data = adapt(song, difficulty='Easy', instrument='five_fret_lead_guitar')
    data['controls'] = CONTROLS
    data['origin'] = 'Chart audio zero plus two-second pre-roll; authoritative hardware audio clock'
    for note in data['notes']:
        note['button'] = CONTROLS[note['lane']]
    data['warnings'] = [w for w in data['warnings'] if not w.startswith((
        'Silence:', 'Genuine sustain durations', 'Only Easy native',
        'HOPO/strum/tap/phrase/text', 'INI sustain_cutoff_threshold')) and 'onset-only play' not in w]
    if data['native_overlap_count']:
        data['warnings'].append('Native same-lane sustain overlaps retained; review existing runtime hold replacement behavior.')
    data['warnings'] += ['Easy native lanes 0/1/2 map to LEFT/B/A; every onset requires a fresh press.',
                         'Source modifiers/phrases and INI gameplay overrides are retained, not applied.']
    return data


def aligned(adapted, audio):
    # Source timestamps include chart/INI offset, before the runtime pre-roll.
    end = max(max(n['start_us'], n['end_us'] if n['genuine_sustain'] else n['start_us'])
              for n in adapted['notes'])
    if end * RATE > audio['source_samples'] * 1_000_000:
        raise ValueError('Audio ends before a note onset or genuine sustain end; select matching audio/offsets.')
    return end


def verify_prepared(folder):
    folder = Path(folder)
    if folder.is_symlink():
        raise ValueError('Prepared directory cannot be a symlink')
    paths = []
    for path in folder.rglob('*'):
        paths.append(path)
        if len(paths) > 32 or (path.is_file() and path.stat().st_size > 32 * 1024**2):
            raise ValueError('Prepared directory exceeds file-count/32MiB-per-file limits')
    if any(p.is_symlink() for p in paths):
        raise ValueError('Prepared files cannot contain symlinks')
    if {p.relative_to(folder).as_posix() for p in paths if p.is_file()} != FILES | {MANIFEST}:
        raise ValueError('Prepared song has missing or unexpected files; prepare into a new directory')
    m = json.loads((folder / MANIFEST).read_text())
    if m.get('schema_version') != SCHEMA or m.get('status') != 'success' or m.get('distribution') != 'private-only':
        raise ValueError('Unsupported or unsuccessful prepared-song manifest')
    if set(m['file_sha256']) != FILES:
        raise ValueError('Prepared file inventory mismatch')
    for name, expected in m['file_sha256'].items():
        if file_hash(folder / name) != expected:
            raise ValueError('Prepared song changed or is damaged: ' + name)
    song = json.loads((folder / 'normalized-song.json').read_text())
    adapted = runtime_adaptation(song)
    if adapted != json.loads((folder / 'adapted.json').read_text()) or header(adapted) != (folder / 'imported_chart.hpp').read_text():
        raise ValueError('Prepared runtime differs from normalized song; prepare again')
    audio = json.loads((folder / 'audio/audio.json').read_text())
    if (m['runtime'] != dict(difficulty='Easy', instrument='five_fret_lead_guitar', physical_controls=CONTROLS,
                             note_heads=adapted['note_count'], genuine_sustains=adapted['genuine_sustain_count']) or
        m['audio'] != dict(mode='reactive' if audio['schema_version'] == 'gba-reactive-audio-v1' else 'fixed',
                           sample_rate=audio['sample_rate'], source_samples=audio['source_samples'],
                           playback_samples=audio['playback_samples'], ffmpeg_version=audio['ffmpeg_version'])):
        raise ValueError('Prepared runtime/audio manifest metadata mismatch')
    if audio.get('prepared_chart_sha256') != file_hash(folder / 'imported_chart.hpp') or audio.get('chart_note_count') != adapted['note_count']:
        raise ValueError('Prepared chart/audio binding mismatch')
    if audio.get('chart_source_sha256') != song['source_sha256'] or audio['pcm_sha256'] != file_hash(folder / 'audio/imported_audio.bin'):
        raise ValueError('Prepared source/audio binding mismatch')
    if audio['sample_rate'] != RATE or audio['source_samples'] <= 0:
        raise ValueError('Unsupported prepared sample rate/count')
    if audio.get('synthetic') is not False:
        raise ValueError('Generic inputs must remain private user-supplied content')
    selected = m['selection']
    if (selected['mode'] not in {'fixed', 'reactive'} or selected['chart'] != song['package']['chart_file'] or
        m['source']['format'] != song['source_format'] or
        m['normalized'] != dict(schema_version=song['schema_version'], timing=song['timing'])):
        raise ValueError('Prepared normalized source/selection metadata mismatch')
    names = selected['mix'] if selected['mode'] == 'fixed' else [selected['guitar']] + selected['backing']
    if selected['mode'] != m['audio']['mode'] or len(names) != len(set(names)) or not 1 <= len(names) <= 8:
        raise ValueError('Invalid explicit audio selection')
    if audio['selected_package_files'] != names or len(audio['sources']) != len(names):
        raise ValueError('Audio selection binding mismatch')
    expected_roles = ['guitar'] + ['backing'] * (len(names) - 1)
    if selected['mode'] == 'reactive' and (len(names) < 2 or [s.get('playback_role') for s in audio['sources']] != expected_roles):
        raise ValueError('Reactive audio role binding mismatch')
    sources = m['source']['selected_files_sha256']
    if tree_digest(sources) != m['source']['selected_tree_sha256'] or sources.get(song['package']['chart_file']) != song['source_sha256']:
        raise ValueError('Selected source inventory mismatch')
    for name, source in zip(names, audio['sources']):
        if source['source_sha256'] != sources.get(name):
            raise ValueError('Decoded audio source hash mismatch')
    aligned(adapted, audio)
    # Reuse strict PCM format/padding/headroom/count validation from the build helper.
    with tempfile.TemporaryDirectory(prefix='gba-song-verify-') as tmp:
        check = Path(tmp)
        shutil.copyfile(folder / 'imported_chart.hpp', check / 'imported_chart.hpp')
        try:
            subprocess.run([sys.executable, str(Path(__file__).with_name('build_audio.py')),
                            '--output-dir', str(check), '--audio-dir', str((folder / 'audio').resolve()),
                            '--private-chart'], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as error:
            raise ValueError(error.stderr.strip() or 'Prepared PCM validation failed') from error
        for name in ['imported_audio.bin', 'imported_backing.bin']:
            if file_hash(check / name) != file_hash(folder / 'audio' / name):
                raise ValueError('Prepared stream mismatch: ' + name)
    return m


def prepare(source, output, *, chart=None, mix=None, guitar=None, backing=None, offset_policy=None):
    source, output = Path(source), Path(output)
    if output.exists():
        raise ValueError('Output must be a new directory; existing prepared songs are never overwritten')
    if source.is_dir() and source.resolve() in output.resolve().parents:
        raise ValueError('Prepared output must be outside the input song folder')
    output.parent.mkdir(parents=True, exist_ok=True)
    diagnostics = []
    try:
        mix, backing = list(mix or []), list(backing or [])
        mode = 'fixed' if mix else 'reactive'
        names = mix if mix else ([guitar] + backing if guitar else [])
        if (not names or len(names) > 8 or len(set(names)) != len(names) or
            (mix and (guitar or backing)) or (not mix and (not guitar or not backing))):
            raise ValueError('Choose --mix FILE(s), or --guitar FILE with --backing FILE(s); 1..8 distinct audio files')
        initial, _ = inspect(source, diagnostics, chart, names, offset_policy)
        selected_chart = initial['package']['chart_file']
        for name in names:
            stream = next(s for s in initial['package']['audio_streams'] if s['file'] == name)
            if stream['role'] == 'preview':
                raise ValueError('Preview audio cannot replace gameplay audio')
        with tempfile.TemporaryDirectory(prefix='.song-', dir=output.parent) as tmp:
            stage = Path(tmp) / 'prepared';stage.mkdir()
            snapshot = Path(tmp) / 'input';snapshot.mkdir()
            selected_files = [selected_chart] + names
            with Package(source) as package:
                selected_files += [n for n in package.entries if PurePosixPath(n).parent == PurePosixPath(selected_chart).parent
                                   and PurePosixPath(n).name.casefold() == 'song.ini']
                source_hashes = {}
                for name in selected_files:
                    data = package.read(name, 128 * 1024**2)
                    path = snapshot / name;path.parent.mkdir(parents=True, exist_ok=True);path.write_bytes(data)
                    source_hashes[name] = digest(data)
            if source_hashes[selected_chart] != initial['source_sha256']:
                raise ValueError('Source chart changed during inspection; retry with stable input')
            # Parse the exact copied bytes subsequently decoded, not live folder files.
            diagnostics = []
            song, _ = inspect(snapshot, diagnostics, selected_chart, names, offset_policy)
            adapted = runtime_adaptation(song)
            audio = (convert_files([snapshot / n for n in names], stage / 'audio') if mix else
                     convert_reactive([snapshot / guitar], [snapshot / n for n in backing], stage / 'audio'))
            if mix:
                (stage / 'audio/imported_backing.bin').write_bytes(bytes(16))
            end = aligned(adapted, audio)
            (stage / 'imported_chart.hpp').write_text(header(adapted))
            audio.update(prepared_chart_sha256=file_hash(stage / 'imported_chart.hpp'),
                         chart_note_count=adapted['note_count'], chart_source_sha256=song['source_sha256'],
                         selected_package_files=names)
            save(stage / 'audio/audio.json', audio)
            save(stage / 'normalized-song.json', song)
            save(stage / 'adapted.json', adapted)
            # Keep source inspection diagnostics in normalized data/report but do
            # not repeat discovery-only claims after actual decoding succeeded.
            warnings = [d for d in diagnostics if d['severity'] == 'warning' and d['code'] not in {'AUDIO_DISCOVERY_ONLY', 'NO_RUNTIME_BINDING', 'SUSTAINS_PREPARED'}]
            if any(d['code'].startswith('DPAD') for d in diagnostics):
                warnings.append(dict(code='INSPECTION_MAPPING', severity='warning',
                    message='Legacy inspection D-pad suggestions are not runtime controls; runtime uses LEFT/B/A.'))
            warnings += [{'code': 'RUNTIME_POLICY', 'severity': 'warning', 'message': w} for w in adapted['warnings']]
            if mix:
                warnings.append(dict(code='FIXED_MIX', severity='warning', message='Fixed mix has no reactive guitar muting; select separate guitar/backing files to enable it.'))
            report = dict(schema_version='gba-song-preparation-report-v1', status='ready', errors=[], warnings=warnings,
                          source_inspection_diagnostics=diagnostics,
                          note_heads=adapted['note_count'], genuine_sustains=adapted['genuine_sustain_count'],
                          last_required_source_us=end, physical_controls=CONTROLS,
                          alignment='All onsets and genuine sustain ends fit decoded audio; human synchronization still needs listening/playtest.',
                          distribution='private-only')
            save(stage / 'validation-report.json', report)
            (stage / 'validation-report.txt').write_text('READY: ' + adapted['title'] + '\n' +
                f"{adapted['note_count']} Easy notes; {adapted['genuine_sustain_count']} sustains; LEFT/B/A; {mode} audio\n" +
                '\n'.join('WARNING ' + w['code'] + ': ' + w['message'] for w in warnings) + '\n')
            manifest = dict(schema_version=SCHEMA, status='success', distribution='private-only',
                source=dict(format=song['source_format'], selected_files_sha256=source_hashes,
                            selected_tree_sha256=tree_digest(source_hashes)),
                selection=dict(mode=mode, chart=selected_chart, mix=mix, guitar=guitar, backing=backing,
                               offset_policy=offset_policy),
                normalized=dict(schema_version=song['schema_version'], timing=song['timing']),
                runtime=dict(difficulty='Easy', instrument='five_fret_lead_guitar', physical_controls=CONTROLS,
                             note_heads=adapted['note_count'], genuine_sustains=adapted['genuine_sustain_count']),
                audio=dict(mode=mode, sample_rate=audio['sample_rate'], source_samples=audio['source_samples'],
                           playback_samples=audio['playback_samples'], ffmpeg_version=audio['ffmpeg_version']),
                file_sha256={n: file_hash(stage / n) for n in sorted(FILES)})
            save(stage / MANIFEST, manifest)
            verify_prepared(stage)
            stage.rename(output)
        return manifest
    except (OSError, ValueError, KeyError, StopIteration, configparser.Error, zipfile.BadZipFile, subprocess.SubprocessError) as error:
        if not output.exists():
            output.mkdir()
            save(output / 'validation-report.json', dict(schema_version='gba-song-preparation-report-v1',
                 status='invalid', errors=[str(error)], warnings=diagnostics))
            (output / 'validation-report.txt').write_text('INVALID: ' + str(error) + '\n')
        raise ValueError(str(error)) from error


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('package', type=Path)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--chart')
    p.add_argument('--mix', action='append', help='Explicit relative audio path; repeat for a fixed mix')
    p.add_argument('--guitar', help='Explicit relative guitar file for reactive audio')
    p.add_argument('--backing', action='append', help='Explicit relative backing file; repeat')
    p.add_argument('--offset-policy', choices=['add', 'ini', 'chart'])
    a = p.parse_args()
    try:
        m = prepare(a.package, a.output, chart=a.chart, mix=a.mix, guitar=a.guitar, backing=a.backing, offset_policy=a.offset_policy)
        print(f"READY: {m['runtime']['note_heads']} Easy notes, {m['audio']['mode']}; manifest {a.output / MANIFEST}")
    except (OSError, ValueError) as error:
        p.exit(1, 'PREPARATION FAILED: ' + str(error) + '\n')


if __name__ == '__main__':
    main()
