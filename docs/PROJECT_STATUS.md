# Mission 001 project status

## Scope and provenance

Work is based on `jellynada/guitar-boy-advance-expanded` at
`6c4e63460fab10733d8ff011045ee246e7201952`. The original repository named by the
owner, `startfliing/guitar-boy-advance`, returned the same HEAD during inspection.
Mission 001 is build and crash prevention only. All existing source and assets
remain; no engine migration or added gameplay systems.

## Architecture

| Part | Responsibility |
| --- | --- |
| `Makefile` | Compile host converter, generate assets, cross-compile ARM7TDMI code, link and fix GBA ROM header |
| `bin/chart_reader.cpp` | Read `.chart` metadata/notes; emit `build/note.h`, song header and ARM assembly |
| `charts/careless.chart` | One ExpertSingle chart, 699 ordered records, lanes 0–3, resolution 192, BPM field 83330 (thousandths), no sustains |
| `music/careless_whisper.mod` | Actual included module, converted by Maxmod's `mmutil`; chart's MP3 filename is unused metadata |
| `graphics/*.png`, `*.grit` | Existing background, fret, note, palette and font art; grit specifies tile/map/palette formats and compression |
| `source/main.cpp` | Video/audio initialization, button handling, frame loop; VBlank callback advances note clock and services audio DMA |
| `include/noteManager.hpp` | Prepare note positions, identify active lanes and hit windows, track hit count/streak |
| `source/sprite.cpp` | Reuse 32 perspective note sprites, depth-sort them, update hardware sprite memory |
| `source/mode7.cpp`, `mode7.iwram.cpp`, `id_sort_shell.s` | Camera projection, perspective background per scanline, affine sprites and depth sort; fast routines in internal RAM |
| `textDisplay`, `font`, `terminal` files | Sprite-based gameplay counters and developer text helpers |

The graphics headers are generated; none of the referenced art is missing.
The chart converter source exists. The CSV converter has only a Windows binary,
but the current game has no CSV inputs. There was no README, CI, test suite or
license file in the baseline checkout.

## The generated note layout

`note.h` was never meant to be downloaded or written by hand. The converter emits:

```cpp
struct Note {
    u64 tick;
    u32 lane;
    u32 duration;
};
```

The assembly emits `.8byte tick`, `.4byte lane`, `.4byte duration`: exactly
16 bytes per record, fields at offsets 0, 8 and 12. Generated compile-time
assertions now verify size and offsets with the actual GBA compiler. Arrays
start on an 8-byte boundary to satisfy that compiler's 64-bit field alignment;
there is no packed struct and no guessed replacement data. The linked chart
symbol should occupy 699 × 16 = 11184 bytes and be divisible by 8.

Timing remains the original conversion `int((chart_tick / resolution) * 3567673)`
using floating point, with the first BPM value driving the per-VBlank song clock.
The existing projection constants, hit windows (3 frames early / 5 late),
10-frame preparation window, module, and controls remain. No timing recalibration
was attempted.

## Implemented behavior retained

- One automatically starting song and four colored lanes.
- Perspective highway with affine note sprites and scanline background effects.
- L/B/A/R rhythm input; visual button highlights and hit-note tile changes.
- Hit-count/total and streak display; Maxmod module playback.
- Music looping and the existing fixed camera mode.

## Mission 001 fixes

- Build a native C++17 chart converter automatically instead of requiring a
  Windows executable on PATH. Keep both original Windows binaries untouched.
- Declare generated `note.h` as a required build product; use grouped Make
  targets so paired chart, graphics and audio outputs are generated once under
  parallel builds. Regenerate a deleted header without manual preparation.
- Verify the generated record layout and align chart arrays correctly.
- Reject missing/zero chart resolution before division.
- Bound the note cursor, hit lookup and sprite lookahead by the song length;
  keep the last note hittable and stop reading nonexistent records afterwards.
- Initialize note positions/palette before the lane switch, and express negative
  note timestamps using signed arithmetic.
- Use a 64-bit highway accumulator: the old signed 32-bit accumulator overflowed
  after roughly seven minutes of continuous running.
- Initialize Maxmod before enabling the callback that services it. Snapshot the
  VBlank-owned sprite cursor and protect hit checking from a partially updated
  64-bit song clock. Rhythm buttons and timing formulas are retained.

## Validation

The tested toolchain is the digest pinned in `scripts/build-docker.sh`: devkitARM
GCC 16.1.0 with its supplied libraries/tools, GNU Make 4.3 and host GCC 12.2.0.
Native cloud builds use an extracted copy of the same GBA toolchain.

- Clean native and container ROM builds, repeat builds, and memory-sanitized
  note-manager/converter tests are performed for this mission. Final measurements
  and checksum are recorded in `docs/BUILD_RESULTS.md`.
- The host regression covers a chord, the final hittable note, a one-note chart,
  and thousands of updates/input checks after the final note. Leak detection is
  disabled only because the original manager intentionally holds two text display
  objects for the process lifetime; address/undefined-behavior checks stay enabled.
- Optional `tests/emulator_smoke.c` uses the real mGBA 0.10.1 core with rendering,
  sampled audio and synthetic four-button presses. It checks the song cursor is
  bounded and reaches 699, changing video frames, nonzero audio samples and no
  emulator core crash. It saves a frame after 1000 frames.
- This is a headless emulator check, not a human playthrough or audio listening
  test. It does not prove every possible RAM access is valid, score correctness,
  physical-cartridge behavior or perfect audiovisual synchronization.

To repeat the optional emulator check on Debian with `gcc` and `libmgba-dev`:

```bash
gcc -O2 tests/emulator_smoke.c -o /tmp/emulator_smoke -lmgba
# Use the address from YOUR matching ELF, not a copied address from an old build.
address=$("$DEVKITARM/bin/arm-none-eabi-nm" guitar-boy-advance-expanded.elf | awk '$3 == "recent_sprite" {print $1}')
/tmp/emulator_smoke guitar-boy-advance-expanded.gba "$address" 699 36000 /tmp/mission001.ppm
```

36000 frames is about ten minutes of emulated GBA time, past both the final note
and the former accumulator overflow point. The 699-note expectation is specific
to this unchanged song. The screenshot is an output asset and is not committed.

## Known bugs and limitations deliberately left for later

- Music loops but notes/score do not reset; reload/reset to replay.
- Repeated presses inside one hit window may count a note more than once; chords
  count as one hit but the denominator counts note records. Misses do not reliably
  reset the streak unless an incorrect button is pressed. Scoring needs its own
  design/fix task; it is not redesigned here.
- Sprite reuse can restore a hit-note tile before its visual lifetime ends.
- The timing conversion is an empirical constant; tempo changes, song offset,
  latency adjustment and arbitrary charts are not supported robustly. Only the
  supplied chart is certified by this mission's checks.
- Developer terminal helpers contain unchecked character/index assumptions and
  legacy formatting quirks; they are not active in the normal game path.
- Process-lifetime heap allocations have no teardown; there is no in-game reload.
- Extended multi-hour playback, save files, physical hardware, and arbitrary
  malformed chart files have not been qualified.
- No menus, multiple songs, star power, sustained-note gameplay, pause/restart UI,
  results screens, fail state, or complete progression system. These are outside
  Mission 001, not promises for this build.
- No project license or complete asset-rights documentation is present. Public
  release needs a rights review with the original creators/asset owners.

## Recommended next development sequence

1. Owner reviews Mission 001 changes and plays the ROM in mGBA. Check all four
   lanes, sound, note arrival and behavior after the last note; record observations.
2. Confirm upstream code, music, chart and artwork redistribution permissions.
3. Agree on a separate scoring-correctness task: one award per note/chord, consistent
   denominator and missed-note handling, with regression tests.
4. Measure song start and drift before proposing any timing/calibration changes;
   preserve this baseline ROM for comparison. Test on physical hardware if available.
5. Add repeatable CI build/testing once repository access and artifact policy are
   approved. Discuss future features only after this baseline is accepted.

Review branch: `mission-001-reproducible-build`. Main must not be merged or reset
automatically. Pull-request creation/publishing status is reported separately;
a local commit is not evidence of an opened PR.
