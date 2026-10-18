# Project status — Mission 002

## Baseline and scope

Mission 002 starts from the working Mission 001 fixes on
`mission-001-reproducible-build`, commit `47d340e`. They have not been silently
replaced with upstream's unpatched code or merged into main. The new source
branch is `mission-002-note-judgment`; its review comparison uses the Mission 001
branch as its base so only the new work is shown.

Mission 001's original baseline was `6c4e63460fab10733d8ff011045ee246e7201952`.
Its historical validation remains in `docs/BUILD_RESULTS.md`. The owner reported
that the Mission 001 ROM worked when played. Mission 002's implementation and
validation are separate; no manual Mission 002 playthrough is claimed.

## Architecture

| Part | Responsibility |
| --- | --- |
| `Makefile`, `scripts/build-docker.sh` | Retained digest-pinned devkitARM C++17 build; compiler-specific chart-converter cache avoids native/container runtime conflicts |
| `bin/chart_reader.cpp` | Unchanged chart conversion, generated headers/assembly, verified 16-byte record layout |
| `include/gameControls.hpp` | Shared physical-button-to-lane mapping: Left, Right, A, B |
| `include/noteJudgment.hpp` | Pure per-note state machine, physical timing windows, edge input, statistics and synchronous gameplay events |
| `include/noteManager.hpp` | Original note-position preparation and ten-frame lookahead; owns judgment without rendering/audio dependencies |
| `source/main.cpp` | Initialization, VBlank frame clock and Maxmod service, main-thread input/judgment, feedback event consumer |
| `source/sprite.cpp` | Existing perspective sprite loading/sorting, persistent hit appearance from judgment state |
| `source/mode7*`, `id_sort_shell.s` | Original perspective background, camera, affine note projection and depth sort |
| `textDisplay`, `font`, `terminal` | Existing font/graphics helpers; textDisplay gains bounded simple labels |
| `charts/careless.chart` | Unchanged 699-note single-tempo chart; sorted lanes 0–3, no chords or sustains |
| `music/`, `graphics/` | Unchanged module audio, palettes, note/fret/background/font art |
| `tests/` | Sanitized host judgment/converter/full-chart tests and real mGBA ROM checks |

## Current gameplay

- Existing four-lane perspective highway, camera, artwork and module playback.
- New controls: **D-pad Left, D-pad Right, A, B**, left to right, as requested by
  the owner; shoulder buttons no longer play notes.
- Per-note Pending, Perfect, Good or Missed state; each note judged once.
- Perfect within 25 ms; Good up to 50 ms early/85 ms late; expired notes become
  automatic misses even when the player presses nothing.
- Fresh presses only; held buttons cannot retrigger notes. Chords are judged
  per member. Extra wrong presses are separate events and cannot consume valid
  notes. See `NOTE_JUDGMENT.md` for the exact partial-chord and boundary rules.
- Minimal PERFECT/GOOD/MISS feedback, H/M counters and a WRONG flash. These are
  diagnostic counters, not a points/multiplier scoring system.
- Hit appearance remains attached to note state during sprite reuse.
- `PerfectHit`, `GoodHit`, `Miss`, `WrongInput` events available to future consumers.

## Mission 001 audit and behavior changes

The generated `note.h` and song/graphics/audio headers are build outputs, not
missing replacement content. `Note` remains 8-byte timestamp, 4-byte lane,
4-byte duration, 16-byte stride, at 8-byte array alignment. Chart conversion and
position constants are unchanged. Maxmod playback remains independent of
judgment, with no new seeking, volume changes or imported song.

The host chart-converter cache now includes its compiler target/version in the
filename. This prevents a binary compiled with cloud GCC 14 from being reused
inside the pinned container, which has GCC 12 and an older C++ runtime. The GBA
toolchain image, converter source/data, and build script remain unchanged.

Mission 001's repeat-hit bug, wrong-button streak reset, chord/total mismatch and
lack of automatic misses are replaced by per-note accounting. Streak text is
replaced with judgment/hit/miss feedback. Newly observed input is checked on the
main thread instead of checking the previous poll against interrupt-owned state.
The late/early allowances are now explicitly in milliseconds and close to the
old five/three-frame windows. These are intentional behavioral differences, not
a timing recalibration. The old projection/lookahead formulas remain.

The pure engine allocates no heap memory and has no renderer or audio calls.
The existing process-lifetime NoteManager allocation remains. No new in-game
restart, menu, score system or audio penalty has been implemented.

## Verified development capabilities

The digest-pinned Mission 001 toolchain and native extracted copy are retained.
Build and emulator outcomes for the final Mission 002 ROM are in
`docs/MISSION_002_RESULTS.md`. Three full ten-minute emulator scenarios exercise
all-success, all-miss and mixed-input play. Desktop tests cover synthetic chords
because the real demo contains none. The updated HUD and original highway were
inspected in emulator screenshots. Samples were measured; nobody listened to
Mission 002 audio or played it manually during this task.

## Remaining limitations and missing features

- Music loops but the chart/judgment does not restart. Reset/reload in mGBA to replay.
- The chart converter's empirical timing constant, first-tempo-only behavior,
  ignored offset metadata and lack of an audio-position clock remain. Human
  audiovisual alignment and latency need measurement before recalibration.
- A physical D-pad cannot normally hold Left+Right together. The supplied chart
  contains no chords, but future charts need to respect this control constraint.
- The engine assumes sorted notes, lanes 0–3 and positive fixed tempo. Arbitrary
  malformed charts, tempo changes and extended multi-hour playback are unqualified.
- Host tests verify isolated reset, not an in-game restart flow. Hardware testing,
  manual keyboard/controller play and audio listening are still outstanding.
- Developer terminal helpers retain legacy unchecked character assumptions;
  the normal HUD uses bounded labels and validated characters instead.
- No sustained-note gameplay, star power, multiple songs, song selection, menus,
  pause UI, results screen, score points/multipliers or reactive audio yet.
- No project license or complete asset-rights records exist in the baseline.
  Existing credits remain. No new song, substitute art or license grant is added.
- GitHub API access previously rejected PR creation, although authenticated Git
  reads/pushes work. Source/download publication and PR-creation outcomes must be
  reported separately; a pushed branch is not an opened pull request.

## Recommended next sequence

1. Owner downloads Mission 002, maps Left/Right/A/B in mGBA, and tries hits, holds,
   wrong presses and letting notes pass. Check H+M reaches 699 at the end.
2. Review source changes against Mission 001 without automatically merging main.
3. Confirm asset/music/code permissions and measure audio/visual alignment before
   any public-release or timing-calibration decision.
4. Mission 003 can subscribe to the existing gameplay events for reactive audio,
   with an explicit per-note/per-chord policy and measured playback-clock alignment.
   It should not rebuild the judgment system or import unapproved music.
5. Add CI and physical-hardware checks as a separate follow-up if desired.
