# Mission 003 evidence

## Branch audit

Mission 003 starts from tested Mission 002 source `5338621`, which contains
Mission 001 (`47d340e`) by verified Git ancestry. At start, main remained the
original `6c4e634`; Mission 001/002 fixes had not been merged. Source and download
branches were inspected separately. No automatic merge into main is performed.

## Importer tests

`bash tests/check.sh` runs all previous Mission 002 sanitizer/699-note checks and
**32 Python importer tests**. Final results, failure status and compiler checks
are included in the bundle logs. AddressSanitizer, UndefinedBehaviorSanitizer and
leak checks remain enabled for the existing C++ judgment tests.

The importer tests cover constant/changing tempos, alternate resolutions,
exact change boundaries, source-order chords, independent difficulties, sustain
integration across tempo changes, positive/negative/fractional offsets, markers,
open notes, signatures, anchors, unknown/unsupported tracks/events, duplicate and
unsorted events, missing/invalid data, overflow, bad UTF-8, generated headers,
determinism, stale-output removal and batch processing past invalid files.

Expected timestamps are hand-calculated, not golden output from the same tool:

| Synthetic case | Independent expected result |
| --- | --- |
| 120 BPM, resolution 100, tick 100 | 500000 us |
| Same, tick 300 | 1500000 us |
| Two beats at 120 BPM, then one at 60 BPM | Boundary times 1 s, then 2 s |
| Additional one beat at 240 BPM, Offset +.25 s | Final time 2.50 s |
| Sustain from tick 192 to 768 in that tempo map | .5 + 1 + .25 = 1.75 s |
| 100 alternating one-tick segments, resolution 3, 120/90 BPM | Exactly 175000000/9 us; export 19444444 us |

Generated prepared headers compiled with both desktop GCC and actual devkitARM
C++17, including ARM7TDMI/Thumb, negative half-microsecond offsets and the signed
64-bit endpoints. No GBA compiler check was skipped in this environment. These
are prepared tables, not a claim that the game already plays imported data.

## Demonstrated workflow

Both commands were executed successfully:

```text
python3 tools/import_chart.py tests/fixtures/charts/tempo_changes.chart
python3 tools/import_chart.py charts/careless.chart
```

The synthetic report identifies Easy/Medium/Hard/Expert independently and flags
five/open-fret, sustain, marker and D-pad limitations. The original demo imports
as 699 ExpertSingle notes, four logical fret slots, no chords or sustains. All
successful imports explicitly report `prepared_not_playable` with no live
runtime/audio binding. Invalid charts produce nonzero exit status, readable
errors, and no stale song/header assets. No supplied user chart was substituted.

## Real game build and regression

Commands actually run:

```text
bash scripts/build-docker.sh clean
bash scripts/build-docker.sh
```

A real Game Boy Advance ROM was produced: **289840 bytes**.

```text
853ccc89e4e6da2b95ba4fa32ab9ca4fc53937fef257d55e2a9f41522ca823e8
```

That SHA-256 is identical to Mission 002. No live converter, game source, controls,
Makefile, art, chart or music changed. Therefore **zero demo note timestamps or
ROM bytes changed**; new absolute-time data remains an isolated output path.
The expected game filename in the bundle is `guitar-boy-advance-mission-003.gba`;
renaming a copy does not change its contents.

The actual mGBA 0.10.1 headless core ran this ROM for 36000 frames (~10 emulated
minutes), using the matching ELF for timing/counter symbols. Exit status was zero:

```text
PASS: 36000 frames, final cursor 699, 35633 changing frames, 39301965 nonzero audio samples, no core crash
PASS: mode perfect, Perfect 699, Good 0, Miss 0, WrongInput 0; every note counted once
PASS: visible hit-tile feedback present for 6081 frames
```

Previous miss/chord/hold/wrong-input behavior is covered by the unchanged
Mission 002 host tests, which were rerun. No manual listening, keyboard play,
hardware testing or audio/visual calibration was performed. This demonstrates
playback/rendering and note accounting activity, not perfect music synchronization.

## Known boundaries

No authorized Sunshine of Your Love chart was supplied. No Cream recording,
commercial GH assets, unauthorized chart or new audio was downloaded or bundled.
Original synthetic fixtures and the already-present demo are the only chart inputs.
No new renderer, difficulty screen, score system, audio compression/muting or
multiple-song selection is implemented. GBA runtime binding of prepared data,
matching licensed recording, pre-roll/offset calibration and future lane rendering
remain explicit next tasks. A GHIII cover chart may not fit Cream's recording.

The readable import and architecture guides describe supported/retained/rejected
features and source conventions. GitHub PR creation/publication outcomes are
reported separately; a branch/comparison alone is not an opened PR.
