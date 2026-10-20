#!/usr/bin/env python3
"""Exercise a verified generic ROM using existing actual-key mGBA regressions."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess

try:
    from .release_common import verify_result
except ImportError:
    from release_common import verify_result


def run(root, build, output, symbols):
    root, build, output, symbols = [Path(p).resolve() for p in (root, build, output, symbols)]
    m = verify_result(build)
    if m['profile'] != 'song':
        raise ValueError('Generic smoke runner requires a verified song-profile build')
    output.mkdir(parents=True, exist_ok=False)
    rom = build / m['rom']
    for name, source in [('identity', 'build_identity_emulator.c'), ('pause', 'pause_emulator.c')]:
        subprocess.run(['gcc', '-O2', '-Wall', '-Wextra', '-Werror', str(root / 'tests' / source),
                        '-o', str(output / name), '-lmgba'], check=True)
    subprocess.run([str(output / 'identity'), str(rom), 'M014 / SONG / LOCAL'], check=True)
    samples = int(re.search(r'imported_audio_playback_samples = (\d+)', (build / 'runtime/imported_audio.hpp').read_text())[1])
    frames = (samples * 1024 + 280895) // 280896 + 120
    env = {k: v for k, v in os.environ.items() if not k.startswith('GBA_')}
    env['GBA_PAUSE_PLAYBACK_SAMPLES'] = str(samples)
    # These acceptance scenarios require a sufficiently long song for 8 cycles.
    # The two supplied examples are sized for this; arbitrary songs may use a
    # targeted driver instead. This runner is not a universal playability gate.
    cases = [0, 12, 17, 19]
    choices=m.get('available_difficulties',[dict(name='Easy',note_heads=m['assets']['note_heads'])])
    for choice,chart in enumerate(choices):
        env['GBA_DIFFICULTY']=str(choice)
        for case in cases:
            prefix = output / f'difficulty-{choice}-pause-{case}'
            with prefix.with_suffix('.log').open('w') as log:
                subprocess.run([str(output / 'pause'), str(rom), str(symbols), str(chart['note_heads']),
                                str(frames), str(case), '1' if case == 0 else '30', str(prefix)],
                               env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
    result = dict(source_commit=m['source_commit'], rom_sha256=m['rom_sha256'], note_heads=m['assets']['note_heads'],
                  frames=frames, cases=cases, difficulties=choices, result='passed', physical_hardware_verified=False)
    (output / 'smoke.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--build', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--symbols', type=Path, required=True, help='nm output from matching ELF')
    a = p.parse_args()
    run(a.repo, a.build, a.output, a.symbols)
