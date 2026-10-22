"""Source and artifact checks shared by the two official build profiles."""
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import zipfile

PUBLIC_DIRS = {'bin', 'charts', 'docs', 'graphics', 'imports', 'include',
               'music', 'scripts', 'source', 'tests', 'tools'}
PUBLIC_WORKFLOWS = {'.github/workflows/foundation.yml', '.github/workflows/public-demo.yml',
                    '.github/workflows/m020-closeout.yml', '.github/workflows/m021-ui.yml', '.github/workflows/m022-collection.yml'}
PUBLIC_DEMO_DELIVERY = {'public-demo-downloads/' + n for n in (
    'Guitar-Boy-Advance-Expanded-v0.1.0-alpha-RC1.gba',
    'Guitar-Boy-Advance-Expanded-v0.1.0-alpha-RC1.zip', 'DELIVERY.json', 'SHA256SUMS.txt',
    'Guitar-Boy-Advance-Expanded-v0.1.0-alpha-RC2.gba',
    'Guitar-Boy-Advance-Expanded-v0.1.0-alpha-RC2.zip', 'RC2-DELIVERY.json', 'RC2-SHA256SUMS.txt')}
PUBLIC_ROOT = {'.gitignore', 'Makefile', 'README.md', 'Build-Cream-ROM.bat'}
PROFILES = {'public': ('public-synthetic', 'Guitar-Boy-Advance-M014-Synthetic.gba'),
            'cream': ('cream-private', 'Guitar-Boy-Advance-M014-Cream-Private.gba'),
            'song': ('song-private', 'Guitar-Boy-Advance-M014-Song-Private.gba')}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_hash(path):
    return digest(Path(path).read_bytes())


def safe_source_name(name):
    p = PurePosixPath(name)
    parts = p.parts
    if not parts or p.is_absolute() or '..' in parts or '\\' in name:
        raise ValueError('Unsafe source path: ' + name)
    lower = [x.lower() for x in parts]
    if any(x in {'private', 'builds', 'build', 'downloads', '.git', '__pycache__'} for x in lower):
        raise ValueError('Private/generated path cannot enter public source: ' + name)
    if len(parts) == 1 and name not in PUBLIC_ROOT:
        raise ValueError('Unreviewed public root file: ' + name)
    if len(parts) > 1 and parts[0] not in PUBLIC_DIRS and name not in PUBLIC_WORKFLOWS:
        raise ValueError('Unreviewed source directory: ' + name)
    if parts[0] == 'imports' and name not in {'imports/incoming/README.md', 'imports/output/README.md'}:
        raise ValueError('Imported private/generated payload: ' + name)
    if p.suffix.lower() in {'.gba', '.elf', '.bin', '.zip', '.wav', '.opus', '.mp3', '.ogg', '.flac', '.pcm', '.raw', '.samples', '.fifo', '.map'}:
        raise ValueError('Generated or recording payload cannot enter public source: ' + name)
    if p.name.lower() in {'audio.json', 'adapted.json', 'imported_chart.hpp', 'imported_audio.hpp', 'song-manifest.json', 'normalized-song.json'}:
        raise ValueError('Prepared song data cannot enter public source: ' + name)
    return name


def tree_digest(files):
    return digest(json.dumps(files, sort_keys=True, separators=(',', ':')).encode())


def source_snapshot(root):
    """Return committed public bytes, never a recursive copy of a working folder."""
    root = Path(root).resolve()
    if (root / '.git').exists():
        def git(*args):
            return subprocess.check_output(['git', '-C', str(root), *args])
        if git('status', '--porcelain', '--untracked-files=no').strip():
            raise ValueError('Tracked source has uncommitted changes. Commit/review them first; no old revision was built.')
        commit = git('rev-parse', 'HEAD').decode().strip()
        files = {}
        with zipfile.ZipFile(io.BytesIO(git('archive', '--format=zip', commit))) as z:
            for entry in z.infolist():
                if entry.is_dir():
                    continue
                # Reviewed public demo delivery is a separate artifact commit,
                # never a source/build input (nor recursively repackaged).
                if entry.filename.startswith('public-demo-downloads/'):
                    if entry.filename not in PUBLIC_DEMO_DELIVERY:
                        raise ValueError('Unreviewed public demo delivery path: ' + entry.filename)
                    continue
                safe_source_name(entry.filename)
                if (entry.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError('Source symlinks require explicit review: ' + entry.filename)
                files[entry.filename] = z.read(entry)
        # Detect edits made while git archive ran; the archive itself is immutable.
        if git('status', '--porcelain', '--untracked-files=no').strip():
            raise ValueError('Source changed while it was being exported; retry after committing.')
    else:
        manifest_path = root / 'SOURCE_MANIFEST.json'
        if not manifest_path.is_file():
            raise ValueError('No Git revision or SOURCE_MANIFEST.json. Extract the complete official review ZIP, not selected files.')
        manifest = json.loads(manifest_path.read_text())
        commit = manifest['source_commit']
        files = {}
        for name, expected in manifest['files'].items():
            safe_source_name(name)
            path = root / name
            if path.is_symlink() or not path.is_file() or file_hash(path) != expected:
                raise ValueError('Source archive changed or is incomplete: ' + name)
            files[name] = path.read_bytes()
        if tree_digest(manifest['files']) != manifest['source_tree_sha256']:
            raise ValueError('Source manifest tree mismatch')
    if not re.fullmatch('[0-9a-f]{40}', commit):
        raise ValueError('Source revision is not a full Git commit')
    hashes = {n: digest(b) for n, b in sorted(files.items())}
    metadata = {'schema': 'gba-source-v1', 'source_commit': commit,
                'source_tree_sha256': tree_digest(hashes), 'files': hashes}
    return files, metadata


def export_source(files, metadata, destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    for name, data in files.items():
        safe_source_name(name)
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    (destination / 'SOURCE_MANIFEST.json').write_text(json.dumps(metadata, indent=2) + '\n')


def validate_assets(work, profile):
    """Validate freshly built runtime bytes, and the private header/audio binding."""
    work = Path(work)
    runtime = work / 'build'
    header = (runtime / 'imported_chart.hpp').read_bytes()
    match = re.search(rb'imported_note_count = (\d+)', header)
    if not match:
        raise ValueError('Missing runtime chart count')
    count = int(match[1])
    synthetic = re.search(rb'imported_is_synthetic = (true|false)', header)
    if not synthetic or (synthetic[1] == b'true') != (profile == 'public'):
        raise ValueError('Wrong public/private runtime chart identity')
    if profile == 'song':
        try:
            from .song_pipeline import verify_prepared
        except ImportError:
            from song_pipeline import verify_prepared
        prepared = work / 'imports/output/song'
        m = verify_prepared(prepared)
        for name in ['imported_chart.hpp', 'audio/imported_audio.bin', 'audio/imported_backing.bin']:
            if file_hash(runtime / Path(name).name) != file_hash(prepared / name):
                raise ValueError('Generic runtime differs from prepared song: ' + name)
        audio = json.loads((prepared / 'audio/audio.json').read_text())
        return {'note_heads': m['runtime']['note_heads'], 'genuine_sustains': m['runtime']['genuine_sustains'],
                'chart_sha256': digest(header), 'guitar_sha256': file_hash(runtime / 'imported_audio.bin'),
                'backing_sha256': file_hash(runtime / 'imported_backing.bin'),
                'source_samples': audio['source_samples'], 'sample_rate': audio['sample_rate'],
                'ffmpeg_version': audio['ffmpeg_version'], 'selected_package_files': audio['selected_package_files']}
    if profile == 'cream':
        prepared = work / 'imports/output/cream'
        adapted = json.loads((prepared / 'adapted.json').read_text())
        audio = json.loads((prepared / 'audio/audio.json').read_text())
        if count != 395 or adapted['note_count'] != 395 or adapted['genuine_sustain_count'] != 78:
            raise ValueError('Cream package must provide395 Easy heads and78 genuine sustains; no substitute was built.')
        if audio.get('prepared_chart_sha256') != digest(header) or audio.get('chart_note_count') != count or file_hash(prepared / 'imported_chart.hpp') != digest(header):
            raise ValueError('Stale chart/audio binding; prepare together again')
        if audio.get('schema_version') != 'gba-reactive-audio-v1' or audio.get('synthetic') is not False:
            raise ValueError('Cream requires actual reactive guitar and backing')
        if len(audio.get('selected_package_files', [])) != 3 or [s['playback_role'] for s in audio['sources']] != ['guitar', 'backing', 'backing']:
            raise ValueError('Wrong explicit stem selection')
        if audio['source_samples'] < 260 * 16384:
            raise ValueError('Cream recording unexpectedly short')
        for filename, key in [('imported_audio.bin', 'pcm_sha256'), ('imported_backing.bin', 'backing_sha256')]:
            if file_hash(runtime / filename) != audio[key] or file_hash(prepared / 'audio' / filename) != audio[key]:
                raise ValueError('Stale/mismatched prepared audio stream: ' + filename)
    else:
        # Generate the original public fixture independently of any ignored inputs.
        try:
            from .chart_importer import normalize
            from .adapt_chart import adapt, header as make_header
            from .reactive_prepare import synthetic_reactive
        except ImportError:
            from chart_importer import normalize
            from adapt_chart import adapt, header as make_header
            from reactive_prepare import synthetic_reactive
        import tempfile
        song = normalize((work / 'tests/fixtures/runtime/easy.chart').read_text(), 'Synthetic Easy Test')
        adapted = adapt(song, difficulty='Easy', instrument='five_fret_lead_guitar', synthetic=True)
        if count != 25 or header != make_header(adapted).encode():
            raise ValueError('Public runtime does not match the original synthetic fixture')
        with tempfile.TemporaryDirectory() as tmp:
            audio = synthetic_reactive(song, tmp)
            for filename in ['imported_audio.bin', 'imported_backing.bin']:
                if file_hash(runtime / filename) != file_hash(Path(tmp) / filename):
                    raise ValueError('Public audio is not the synthetic fixture')
    return {'note_heads': count, 'genuine_sustains': adapted['genuine_sustain_count'],
            'chart_sha256': digest(header), 'guitar_sha256': file_hash(runtime / 'imported_audio.bin'),
            'backing_sha256': file_hash(runtime / 'imported_backing.bin'),
            'source_samples': audio['source_samples'], 'sample_rate': audio['sample_rate'],
            'ffmpeg_version': audio.get('ffmpeg_version', 'not used: integer synthetic generator'),
            'selected_package_files': audio.get('selected_package_files', [])}


def verify_result(folder, public_only=False):
    """Require a successful exact artifact identity before presenting or packaging it."""
    folder = Path(folder)
    m = json.loads((folder / 'manifest.json').read_text())
    if m.get('schema') != 'gba-build-v1' or m.get('status') != 'success':
        raise ValueError('No successful build manifest')
    profile = m['profile']
    if profile not in PROFILES or (public_only and profile != 'public'):
        raise ValueError('A private build cannot enter a public package')
    label, filename = PROFILES[profile]
    if m['rom'] != filename or not re.fullmatch('[0-9a-f]{40}', m['source_commit']):
        raise ValueError('Build filename/revision mismatch')
    required = {filename, filename.replace('.gba', '.elf'), 'runtime/imported_chart.hpp',
                'runtime/imported_audio.bin', 'runtime/imported_backing.bin', 'runtime/imported_audio.hpp'}
    if set(m['artifact_sha256']) != required:
        raise ValueError('Incomplete build artifact inventory')
    for name, expected in m['artifact_sha256'].items():
        if name not in {filename, filename.replace('.gba', '.elf'), 'runtime/imported_chart.hpp',
                        'runtime/imported_audio.bin', 'runtime/imported_backing.bin', 'runtime/imported_audio.hpp'}:
            raise ValueError('Unexpected build payload: ' + name)
        if file_hash(folder / name) != expected:
            raise ValueError('Stale or damaged build output: ' + name)
    data = (folder / filename).read_bytes()
    marker = f'GBA_BUILD:M014:{label}:{m["source_commit"]}'.encode() + b'\0'
    if data.count(marker) != 1 or len(data) != m['rom_bytes'] or file_hash(folder / filename) != m['rom_sha256']:
        raise ValueError('ROM identity/hash/size does not match manifest')
    for stem, key in [('imported_chart.hpp', 'chart_sha256'), ('imported_audio.bin', 'guitar_sha256'), ('imported_backing.bin', 'backing_sha256')]:
        if file_hash(folder / 'runtime' / stem) != m['assets'][key]:
            raise ValueError('Manifest runtime asset mismatch')
    if profile == 'song':
        try:
            from .song_pipeline import verify_prepared
        except ImportError:
            from song_pipeline import verify_prepared
        prepared = folder / 'prepared'
        song = verify_prepared(prepared)
        if file_hash(prepared / 'song-manifest.json') != m.get('prepared_song_sha256'):
            raise ValueError('Build prepared-song manifest mismatch')
        expected_choices=song['runtime'].get('difficulties',[dict(name=song['runtime']['difficulty'],note_heads=song['runtime']['note_heads'],physical_controls=song['runtime']['physical_controls'])])
        if ('available_difficulties' in m or song['schema_version']=='gba-prepared-song-v2') and m.get('available_difficulties')!=expected_choices:
            raise ValueError('Build difficulty inventory differs from preparation')
        if song['runtime']['note_heads'] != m['assets']['note_heads'] or song['runtime']['genuine_sustains'] != m['assets']['genuine_sustains']:
            raise ValueError('Build prepared-song counts mismatch')
        for name in ['imported_chart.hpp', 'audio/imported_audio.bin', 'audio/imported_backing.bin']:
            if file_hash(folder / 'runtime' / Path(name).name) != file_hash(prepared / name):
                raise ValueError('Build runtime differs from prepared song')
        for name in ['imported_audio.bin', 'imported_backing.bin']:
            if (folder / 'runtime' / name).read_bytes() not in data:
                raise ValueError('Prepared audio stream missing from ROM')
    if public_only:
        if m['assets']['note_heads'] != 25 or m['assets']['genuine_sustains'] != 6 or m.get('input_zip_sha256') is not None:
            raise ValueError('Public manifest contains private configuration')
        # Require both verified public PCM streams and the chart inside the ROM.
        for filename in ['imported_chart.hpp', 'imported_audio.bin', 'imported_backing.bin']:
            if filename.endswith('.bin') and (folder / 'runtime' / filename).read_bytes() not in data:
                raise ValueError('Public PCM missing from ROM')
    return m
