#!/usr/bin/env python3
"""Generate labels only; no profile-specific game logic."""
import argparse
from pathlib import Path
import re

LABELS = {'legacy': 'M012 REVIEW', 'public-synthetic': 'M012 / SYNTH',
          'cream-private': 'M012 / CREAM / LOCAL'}


def identity(profile, revision):
    if profile not in LABELS or not re.fullmatch(r'[0-9a-f]{40}|unversioned', revision):
        raise ValueError('Invalid build profile/source revision')
    return ('// Generated build identity, not a gameplay configuration.\n#pragma once\n'
            f'#define GBA_BUILD_TITLE "{LABELS[profile]}"\n'
            f'#define GBA_BUILD_MARKER "GBA_BUILD:M012:{profile}:{revision}"\n')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--profile', choices=LABELS, required=True)
    p.add_argument('--revision', required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    content = identity(a.profile, a.revision)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    if not a.output.exists() or a.output.read_text() != content:
        a.output.write_text(content)
