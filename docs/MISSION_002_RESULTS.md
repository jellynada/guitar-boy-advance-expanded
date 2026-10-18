# Mission 002 build and test results

## Final ROM

Built successfully from Mission 001's fixed baseline with the same digest-pinned
devkitARM toolchain. No art, module music, chart data, converter timing formula,
projection formula or audio-volume code was changed.

Source-build artifact:
`/workspace/guitar-boy-advance-expanded/guitar-boy-advance-expanded.gba`

Download copy: `guitar-boy-advance-mission-002.gba` in the Mission 002 bundle.
The different filename is only to distinguish it from the previous download.

Size: **289840 bytes**. SHA-256 of both copies:

```text
853ccc89e4e6da2b95ba4fa32ab9ca4fc53937fef257d55e2a9f41522ca823e8
```

Verified build commands:

```bash
bash scripts/build-docker.sh clean
bash scripts/build-docker.sh
```

Also verified a clean native `make -j2` using the extracted GBA toolchain,
regeneration after deleting `build/note.h`, and switching back to Docker after
the native build. All produced the same ROM checksum. The first switch exposed
a cached desktop-converter ABI problem (cloud GCC 14 binary inside GCC 12's
container runtime); compiler-specific helper filenames fixed it. No verification
or tests were disabled. The pinned image and build script remain the Mission 001
versions. Compiler: devkitARM GCC 16.1.0, C++17; Make 4.3 in the container.

Directly reading all 699 linked 16-byte records from this ROM matched the
unchanged chart's timestamp conversion, lane and duration. The linked array is
8-byte aligned. The original generated-layout assertions still pass.

## Desktop automated tests

`bash tests/check.sh` completed with exit code zero. AddressSanitizer and
UndefinedBehaviorSanitizer are enabled with fatal failures and leak detection.

```text
PASS: timing boundaries, misses, wrong/extra input, chords, holds, repeat prevention, reset, final/empty charts, controls
PASS: ASan/UBSan judgment checks; 699 chart records and unchanged timing; invalid resolution rejected
PASS: unchanged 699-note chart, all-miss and all-perfect runs, exactly one event per note, consistent stats
```

Coverage includes intended timestamps, exact inclusive timing boundaries and
just-outside boundaries, tempo-independent millisecond windows, early/late
input, automatic misses, unrelated/extra buttons, simultaneous and partial
chords, held input, close repeated notes, duplicate attempts, zero-time/final/
empty charts, reset including held-button history, event payloads and requested
Left/Right/A/B mapping. The full demo runs verify all 699 note states and exactly
one judgment event per note, both with no input and with scheduled correct input.

## Actual mGBA tests

The final checksum above identifies the ROM used in three mGBA **0.10.1**
headless-core runs. Each executed **36000 frames**, approximately **10 minutes**
of emulated GBA time. The runner obtains RAM/ROM addresses from the matching ELF,
injects the real Left/Right/A/B hardware bits, checks statistics throughout and
requires all 699 notes to be judged by the end. All three exited successfully.

| Input scenario | Perfect | Good | Missed | WrongInput events |
| --- | ---: | ---: | ---: | ---: |
| Scheduled correct presses | 699 | 0 | 0 | 0 |
| No input | 0 | 0 | 699 | 0 |
| Mixed presses every 30 frames | 85 | 123 | 491 | 1199 |

WrongInput events are separate mistakes, not additional missed notes. In every
row Perfect + Good + Missed equals 699. The visual cursor reached 699 and stayed
bounded. No emulator core crash occurred, including after the final note.

| Scenario | Changing video frames | Nonzero stereo sample values |
| --- | ---: | ---: |
| Scheduled correct presses | 35633 | 39301965 |
| No input | 35633 | 39301880 |
| Mixed presses | 35665 | 39301966 |

The scheduled-correct-input run also verified **6081 frames** with an unhidden
note sprite using the original successful-hit tile in actual GBA sprite memory.
This checks the note feedback path beyond the counter display.

Captured frames were visually inspected: the existing highway and fret circles
remain, with PERFECT/GOOD/MISS, H/M counters and the separate WRONG indicator
shown in the relevant scenarios. The supplied chart has no chords; chord logic
is tested on synthetic host fixtures, not claimed as a demo-chart emulator case.

## What this does not establish

No person manually played this Mission 002 ROM, listened to its audio, calibrated
latency, or tested physical GBA hardware during this task. Nonzero audio samples
and unchanged module data demonstrate playback activity, not a listening or
musical-synchronization judgment. Emulator input bypasses the frontend's keyboard
configuration and opposing-direction filter. No extended multi-hour test was run.
Music still loops without restarting the chart. No reactive audio, new song,
menus, sustain gameplay, star power or score multipliers were added.

## Reproduce or try it yourself

Developers can run the commands in `docs/NOTE_JUDGMENT.md` to reproduce the host
and emulator scenarios. Non-programmers should download the Mission 002 bundle,
open `guitar-boy-advance-mission-002.gba` in mGBA, map Left/Right/A/B, and follow
the short checks in the README. The Mission 001 download remains available as
the known working baseline.
