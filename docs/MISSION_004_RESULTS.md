# Mission 004 — measured results

## Baseline and scope

Started from Mission003 source `135a55c2a0de50a4c68610f1aeb288924508bb54`,
which contains Mission002 and Mission001 by Git ancestry. Remote main checked
with `git ls-remote` remains `6c4e63460fab10733d8ff011045ee246e7201952`.
Work is on `mission-004-universal-import`. No automatic merge.

New code is computer-side only. No original chart, music, graphics, C++ game,
judgment window, control mapping, renderer, converter or Makefile changed.
Python standard library only, Python3.10+; actual checks used Python3.12.14.
The old chart CLI gained package/module-compatible imports; its behavior remains.

## Automated validation actually run

```bash
export DEVKITPRO=/workspace/.cloud-setup/gba/devkitpro
export DEVKITARM="$DEVKITPRO/devkitARM"
export PATH="$DEVKITARM/bin:$DEVKITPRO/tools/bin:$PATH"
bash tests/check.sh
```

- **32** existing chart-importer tests passed, including native and real
  ARM7TDMI/Thumb generated-header compilation. No skips.
- **34** new MIDI/package tests passed: Type0/1, four difficulties, tempo changes,
  exact boundaries, non-integral milli-BPM, running status, zero-velocity offs,
  per-channel pairing, chords and tempo-crossing sustains, markers, SysEx retention,
  enhanced opens, bass and raw drums, unknown pitches, track identification,
  truncated every-prefix MIDI, bad headers/data/tempo/meter patterns, limits,
  metadata/encoding, signed fractional offsets, explicit offset/audio/chart choices,
  multiple stems and formats, ZIP/folder equivalence, safe archive/folder paths,
  decompression/entry/read limits, deterministic output and stale-output removal.
- Existing ASan/UBSan/leak checks passed: timing boundaries, holds, wrong/extra
  input, partial/full chords, one-time judgments, reset, empty/final charts,
  controls and complete 699-note all-hit/all-miss runs. Legacy conversion unchanged.

Independent timing example: PPQ192 with500000us/q until tick384,
1000000us/q to576, then250000us/q. Medium starts at ticks192/384/384/576
are500000/1000000/1000000/2000000us. Sustain192→768 lasts1750000us,
ending2250000us. INI delay+250ms moves endpoints by250000us, never duration.
Equivalent `.chart`/MIDI fixtures match these independently asserted values.

Actually executed both documented example commands:

```text
python3 tools/import_song.py tests/fixtures/midi
python3 tools/import_chart.py tests/fixtures/charts/tempo_changes.chart
```

Synthetic fixture has no audio and correctly reports it missing. All four
MIDI difficulties are detected, Medium4notes/1chord, tempo points3, meter1.
No third-party chart/audio was added to the tests or output examples.

## Actual ROM builds

Performed a clean native `make clean` then `make -j2`, and separately:

```bash
bash scripts/build-docker.sh clean
bash scripts/build-docker.sh
```

Both produced `guitar-boy-advance-expanded.gba` in the repository root,
**289840 bytes**, SHA256:

```text
853ccc89e4e6da2b95ba4fa32ab9ca4fc53937fef257d55e2a9f41522ca823e8
```

This exactly matches Missions002/003. Official pinned devkitPro image:
`devkitpro/devkitarm@sha256:116afba8df8453961de2936ffab20dd441edf4d682856c1ec8b0e53d7ed0bbf5`,
devkitARM r68/GCC16.1.0, Tonc1.4.5, Maxmod-GBA1.0.15. Host nativeGCC14.2,
container hostGCC12.2. Existing compiler-specific converter caching works.

## Actual emulator regression

mGBA0.10.1 through `tests/run_emulator.sh`, matching ROM/ELF symbols,
**36000 frames in each mode** (about ten minutes of game time):

| Input | Perfect | Good | Miss | Wrong presses |
| --- | ---: | ---: | ---: | ---: |
| perfect | 699 | 0 | 0 | 0 |
| miss | 0 | 0 | 699 | 0 |
| mixed | 85 | 123 | 491 | 1199 |

All runs: final cursor699, bounded counters, no core crash, changing framebuffer
and nonzero stereo audio samples. Perfect/mixed visible hit-tile feedback
6081/1731frames. Nonzero samples39301965/39301880/39301966 respectively.
These verify the existing demo only. No manual listening/keyboard play, hardware
play, latency calibration or actual imported-song playback is claimed.

## Target package and limitations

`Cream (WaveGroup) - Sunshine of Your Love (Neversoft).zip` was not in the
workspace/attachments. No real compatibility result or note/difficulty count for
it is claimed. Run the private command in `SONG_PACKAGE_IMPORT.md`. No outside
chart/audio package was downloaded or publicly committed.

MIDI supports explicit PPQ tempos and named five-fret tracks, not every possible
MIDI/CloneHero extension. SysEx/unknown events are retained, not executed/applied.
Automatic HOPOs, sustain cutoff, marker precedence and INI mechanical policies
need a later adapter. Audio identification is filename/extension discovery only.
New data is normalized JSON, **not playable**; the old chart-only header remains
separate. No new menus, scores, fretboards, reactive audio or compression.

## Review handoff

Source review base: `mission-003-chart-importer`; head:
`mission-004-universal-import`. Download branch: `mission-004-download`, kept
separate from source and never merged. PR creation outcome is recorded below
after the actual attempt. A compare page is not an opened pull request.

Source implementation `4fa807c` was committed and pushed successfully. Actual
`gh pr create --draft --base mission-003-chart-importer --head mission-004-universal-import`
returned `Post "https://api.github.com/graphql": Forbidden`. **No pull request
was opened.** Git push works; no extra credential was requested. Prepared title
and description are in the review bundle's `PULL_REQUEST.md`.

Review/create page:
https://github.com/jellynada/guitar-boy-advance-expanded/compare/mission-003-chart-importer...mission-004-universal-import

Choose Create pull request and paste the prepared description if your GitHub
account permits it. This reviews Mission004 on top of Mission003; it does not
merge the dependency chain into main. The separate download branch contains the
same tested ROM and standalone importer/tools/examples plus evidence logs.
