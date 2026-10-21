#!/usr/bin/env python3
"""Run existing mGBA identity/pause tests on an extracted public ROM, no rebuild."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess

try:
    from .release_common import file_hash, verify_result
except ImportError:
    from release_common import file_hash, verify_result


def run(root, build, extracted, output, symbols):
    root, build, extracted, output = map(Path, (root, build, extracted, output))
    manifest = verify_result(build, public_only=True)
    rom = extracted / manifest['rom']
    if file_hash(rom) != manifest['rom_sha256']:
        raise ValueError('Extracted ROM differs from successful build')
    output.mkdir(parents=True, exist_ok=False)
    for name, source in [('identity', 'build_identity_emulator.c'), ('pause', 'pause_emulator.c'), ('readiness', 'readiness_emulator.c')]:
        subprocess.run(['gcc', '-O2', '-Wall', '-Wextra', '-Werror', str(root / 'tests' / source),
                        '-o', str(output / name), '-lmgba'], check=True)
    subprocess.run([str(output / 'identity'), str(rom), 'M014 / SYNTH'], check=True)
    samples = re.search(r'imported_audio_playback_samples = (\d+)', (build / 'runtime/imported_audio.hpp').read_text())[1]
    env = os.environ.copy()
    # Do not inherit manual fault/silent test knobs into acceptance runs.
    for key in list(env):
        if key.startswith('GBA_'):
            del env[key]
    env['GBA_PAUSE_PLAYBACK_SAMPLES'] = samples
    subprocess.run([str(output / 'readiness'), str(rom), str(symbols)], env=env, check=True)
    # Full synthetic song: single pause, eight cycles, SELECT exit, uninterrupted.
    cases = [0, 12, 17, 19]
    for case in cases:
        prefix = output / f'pause-{case}'
        with prefix.with_suffix('.log').open('w') as log:
            subprocess.run([str(output / 'pause'), str(rom), str(symbols), '25', '1800',
                            str(case), '1' if case == 0 else '30', str(prefix)],
                           env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
    receipt = dict(schema='gba-ci-smoke-v1', source_commit=manifest['source_commit'],
                   rom_sha256=file_hash(rom), visible_identity='M014 / SYNTH',
                   pause_cases=cases, readiness_epochs=20, result='passed', physical_hardware_verified=False)
    (output / 'smoke.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--build', type=Path, required=True)
    p.add_argument('--extracted', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--symbols', type=Path, required=True, help='nm output from the matching verified ELF')
    a = p.parse_args()
    run(a.repo.resolve(), a.build.resolve(), a.extracted.resolve(), a.output.resolve(), a.symbols.resolve())
