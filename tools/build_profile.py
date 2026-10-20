#!/usr/bin/env python3
"""Official fresh, pinned public-synthetic / private-Cream builds. Never uploads."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import uuid

try:
    from .release_common import (PROFILES, export_source, file_hash, source_snapshot,
                                 validate_assets, verify_result)
except ImportError:
    from release_common import (PROFILES, export_source, file_hash, source_snapshot,
                                validate_assets, verify_result)


def utc():
    return datetime.now(timezone.utc).isoformat()


def checked(command, *, cwd, log, env):
    result = subprocess.run(command, cwd=cwd, env=env, stdout=log, stderr=subprocess.STDOUT)
    log.flush()
    if result.returncode:
        print('\n'.join(Path(log.name).read_text(errors='replace').splitlines()[-24:]), file=sys.stderr)
        raise ValueError(f'Command failed (exit{result.returncode}): {command[0]}. Read build.log. '
                         'For Docker, start Docker Desktop and enable Ubuntu WSL integration.')


def build(root, profile, input_zip=None):
    root = Path(root).resolve()
    output = root / 'builds' / ('public' if profile == 'public' else 'private')
    output.mkdir(parents=True, exist_ok=True)
    latest = output / 'LATEST.txt'
    # Invalidate success selection before even checking input, while preserving dated builds.
    latest.unlink(missing_ok=True)
    attempt = {'status': 'building', 'started_utc': utc(), 'profile': profile}
    status = output / 'LAST_ATTEMPT.json'
    status.write_text(json.dumps(attempt, indent=2) + '\n')
    job = Path(tempfile.mkdtemp(prefix='.work-', dir=output))
    log_path = job / 'build.log'
    try:
        if profile == 'cream':
            input_zip = Path(input_zip or root / 'private/Cream.zip').resolve()
            if not input_zip.is_file():
                raise ValueError('Missing private/Cream.zip. Put your existing Cream song ZIP there; '
                                 'enable Windows file extensions and check for Cream.zip.zip. Nothing was substituted.')
            input_hash = file_hash(input_zip)
        else:
            if input_zip is not None:
                raise ValueError('Public builds do not accept private inputs')
            input_hash = None
        files, source = source_snapshot(root)
        input_times = [max((root / n).stat().st_mtime_ns for n in files)]
        if input_zip:
            input_times.append(input_zip.stat().st_mtime_ns)
        export_source(files, source, job / 'engine')
        work = job / 'engine'
        # Use the pinned source's driver/tools, not ignored helpers in the caller folder.
        for executable in ['docker', 'bash'] + (['ffmpeg'] if profile == 'cream' else []):
            if shutil.which(executable) is None:
                raise ValueError(f'Missing {executable} in Ubuntu. See docs/WINDOWS_PRIVATE_BUILD.md. '
                                 'Docker Desktop must expose docker inside WSL.')
        env = os.environ.copy()
        for key in ['MAKEFLAGS', 'MFLAGS', 'MAKEOVERRIDES', 'IMPORTED_HEADER', 'AUDIO_DIR',
                    'BUILD_PROFILE', 'SOURCE_REVISION', 'OUTPUT', 'BUILD', 'TARGET']:
            env.pop(key, None)
        label, rom_name = PROFILES[profile]
        with log_path.open('w') as log:
            print(f'Building M012 / {label} from {source["source_commit"]}', flush=True)
            checked(['docker', 'info'], cwd=work, log=log, env=env)
            if profile == 'cream':
                shutil.copyfile(input_zip, work / 'Cream.zip')
                checked([sys.executable, 'tools/prepare_song.py', 'Cream.zip', '--reactive',
                         '--guitar-stem', 'guitar', '--backing-stem', 'rhythm', '--backing-stem',
                         'song', '--output-dir', 'imports/output/cream'], cwd=work, log=log, env=env)
                header = 'imports/output/cream/imported_chart.hpp'
                audio = 'imports/output/cream/audio'
            else:
                header = audio = ''
            compile_start = time.time_ns()
            checked(['bash', 'scripts/build-docker.sh', f'BUILD_PROFILE={label}',
                     'SOURCE_REVISION=' + source['source_commit'], 'IMPORTED_HEADER=' + header,
                     'AUDIO_DIR=' + audio], cwd=work, log=log, env=env)
            assets = validate_assets(work, profile)
            image = (work / 'scripts/toolchain-image.txt').read_text().strip()
            compiler = subprocess.check_output(['docker', 'run', '--rm', image,
                                                '/opt/devkitpro/devkitARM/bin/arm-none-eabi-gcc', '--version'], env=env, text=True).splitlines()[0]
            (job / 'toolchain.txt').write_text(compiler + '\n' + image + '\n')
        rom = work / 'guitar-boy-advance-expanded.gba'
        elf = work / 'guitar-boy-advance-expanded.elf'
        if not rom.is_file() or not elf.is_file() or min(rom.stat().st_mtime_ns, elf.stat().st_mtime_ns) < compile_start:
            raise ValueError('Compiler did not produce fresh ROM/ELF outputs; old files are not accepted.')
        if rom.stat().st_mtime_ns < max(input_times):
            raise ValueError('ROM is older than a build input. Check your system clock; no stale success was selected.')
        # Recheck caller inputs after compiling, not just the isolated snapshot.
        _, current = source_snapshot(root)
        if current != source or (input_zip and file_hash(input_zip) != input_hash):
            raise ValueError('Source or Cream.zip changed during the build; retry with unchanged inputs.')
        shutil.copy2(rom, job / rom_name)
        elf_name = rom_name.replace('.gba', '.elf')
        shutil.copy2(elf, job / elf_name)
        runtime = job / 'runtime'
        runtime.mkdir()
        for name in ['imported_chart.hpp', 'imported_audio.hpp', 'imported_audio.bin', 'imported_backing.bin']:
            shutil.copy2(work / 'build' / name, runtime / name)
        if profile == 'cream':
            for name in ['adapted.json', 'adaptation_report.txt']:
                shutil.copy2(work / 'imports/output/cream' / name, runtime / name)
            shutil.copy2(work / 'imports/output/cream/audio/audio.json', runtime / 'audio.json')
        artifact_names = [rom_name, elf_name] + ['runtime/' + p.name for p in runtime.iterdir() if p.suffix not in {'.json', '.txt'}]
        manifest = {'schema': 'gba-build-v1', 'status': 'success', 'game_version': 'M012',
                    'profile': profile, 'build_identity': 'M012 / SYNTH' if profile == 'public' else 'M012 / CREAM / LOCAL',
                    'source_commit': source['source_commit'], 'source_tree_sha256': source['source_tree_sha256'],
                    'created_utc': utc(), 'input_zip_sha256': input_hash, 'assets': assets,
                    'toolchain_image': image, 'compiler': compiler, 'rom': rom_name,
                    'rom_bytes': rom.stat().st_size, 'rom_sha256': file_hash(rom),
                    'fresh_outputs': True, 'artifact_sha256': {n: file_hash(job / n) for n in artifact_names}}
        (job / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        (job / 'SOURCE_MANIFEST.json').write_text(json.dumps(source, indent=2) + '\n')
        verify_result(job, public_only=profile == 'public')
        shutil.rmtree(work)
        name = source['source_commit'][:12] + '-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:6]
        result = output / name
        job.rename(result)
        latest.write_text(name + '\n')
        attempt.update(status='success', output=name, finished_utc=utc())
        status.write_text(json.dumps(attempt, indent=2) + '\n')
        print(f'BUILD SUCCESS: {manifest["build_identity"]}\nSource: {source["source_commit"]}\n'
              f'ROM: {result / rom_name}\nSHA-256: {manifest["rom_sha256"]}\n'
              f'Manifest: {result / "manifest.json"}', flush=True)
        if profile == 'cream':
            print('Private local build only. No upload performed. Open the new ROM in mGBA or copy it to your flash cartridge.', flush=True)
        return result
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        # Preserve the log, not a potentially valid-looking old/partial game.
        failure = output / ('.failed-' + job.name.removeprefix('.work-'))
        failure.mkdir()
        if log_path.exists():
            shutil.copy2(log_path, failure / 'build.log')
        attempt.update(status='failed', error=str(error), finished_utc=utc(), log=str(failure / 'build.log'))
        status.write_text(json.dumps(attempt, indent=2) + '\n')
        shutil.rmtree(job, ignore_errors=True)
        raise ValueError(f'{error}\nNo new ROM was delivered. Previous dated builds are unchanged.\nDetails: {status}') from error


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('profile', choices=PROFILES)
    p.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--input', type=Path, help='Existing owner ZIP; cream profile only')
    a = p.parse_args()
    try:
        build(a.repo, a.profile, a.input)
    except (ValueError, OSError) as error:
        print('BUILD STOPPED: ' + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
