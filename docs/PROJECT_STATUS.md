# Project status — Mission 003

## Branches and preserved baseline

Mission 003 starts at tested Mission 002 source commit
`533862124079a9dca1f84a6d88f54e40cde189cb`, on `mission-003-chart-importer`.
Mission 002 contains Mission 001: ancestry was verified with Git, not inferred
from branch names. All repository branches were listed/checked; download branches
contain binaries separately from source review branches.

| Branch | Role / state at Mission 003 start |
| --- | --- |
| `main`, original `work` checkout | Original `6c4e634`; no mission fixes merged |
| `mission-001-reproducible-build` | `47d340e`, working native/pinned builds and end-of-song safety |
| `mission-001-download` | Preserved original tested download |
| `mission-002-note-judgment` | `5338621`, reliable judgment, Left/Right/A/B, unchanged demo |
| `mission-002-download` | Preserved Mission 002 download |
| `mission-003-chart-importer` | New source work; based on Mission 002, not main |

No automatic merge into main is performed. The future target is now **Sunshine
of Your Love by Cream**, superseding the earlier long-term song/audio plan. This
mission prepares community charts only; it does not import a target song or
implement reactive audio.

## Current game — unchanged

The same 699-note Careless Whisper demo, module, art, perspective highway, camera,
button animations and **D-pad Left / D-pad Right / A / B** controls remain.
Mission 002's per-note Pending/Perfect/Good/Missed states, 25 ms Perfect,
50 ms early/85 ms late Good, fresh-press input, chord rules, hit/miss counters,
WRONG indicator and gameplay event interface are preserved. No gameplay source,
converter, Makefile, toolchain image, chart, graphics or music changed.

A clean ROM build has exactly the Mission 002 checksum. New imports are not
wired into its legacy clock or compiled by the default Makefile. No new three/
five-lane renderer, difficulty menu, song selection, audio changes or scoring was
added. The owner can continue using the known working game while data work proceeds.

## New importer architecture

| Component | Responsibility |
| --- | --- |
| `tools/chart_importer.py` | Parse/validate metadata/events, exact cumulative tempo map, normalized data, compatibility analysis and prepared header |
| `tools/import_chart.py` | One-command file/folder workflow, readable/JSON reports, managed outputs and error exit status |
| `imports/incoming/` | User-supplied authorized charts; ignored by Git |
| `imports/output/` | Per-chart reports, normalized JSON and C++17 tables; ignored by Git |
| `tests/fixtures/charts/` | Original synthetic charts with independently calculated expected timestamps; no audio |
| `tests/test_chart_importer.py` | Math, parsing, validation, CLI/determinism/failure cases and host/GBA header compilation |
| `tests/check.sh` | Existing judgment/sanitizer/699-note tests plus new importer suite |

See `CHART_IMPORT_GUIDE.md` for beginner commands and compatibility warnings.
See `SONG_DATA_ARCHITECTURE.md` for the old-converter audit, new schema, exact
timing model, offset convention and integration boundaries.

## Supported versus prepared versus playable

- Metadata, resolution, all BPM changes, boundary timing, signed decimal Offset,
  meter metadata, source-order chords and tempo-aware sustain durations are parsed.
- Easy/Medium/Hard/Expert Single tracks stay independent. Logical frets 0–4 and
  open notes are retained; HOPO/tap markers are separate records, not fake notes.
- Phrases, text, anchors and unknown instrument rows are retained with explicit
  warnings. Not every retained feature has gameplay semantics or header tables.
- Duplicate/unsorted/malformed/overflowing supported events fail clearly rather
  than being silently fixed or dropped. Unknown note types are errors.
- Future layout reports identify Easy 3, Medium 4 and Hard 5 button arrangements,
  fret-count mismatches, opposing D-pad chords and diagonals. Lanes are not collapsed.
- Successful import means **prepared, not playable**. Even four-lane note-shape
  compatibility does not enable the new clock, recording or audio adapter.

## Validation and limitations

`MISSION_003_RESULTS.md` records actual test counts, math examples, build logs,
checksum identity and mGBA results. Generated headers compile on both desktop C++
and devkitARM ARM7TDMI/Thumb. The original 699-note chart is valid in the new
pipeline, while all live note timestamps remain exactly unchanged.

No authorized Sunshine of Your Love chart was supplied; none was downloaded,
fabricated or substituted. No Cream audio or official Guitar Hero assets were
obtained. Tests use original synthetic fixtures and the existing checked-in demo.
A GHIII cover chart must not be assumed to match Cream's original performance.

Remaining data/runtime work:

- An explicit absolute-time gameplay adapter, audio-origin/pre-roll policy,
  calibration and measured beginning/middle/end alignment.
- Approved three/five-lane renderers and difficulty selection; Expert is not
  automatically renamed Hard, and five-lane community charts are not reduced.
- `song.ini` metadata/delay overrides, MIDI and other instruments are not applied.
- Anchors are editor metadata; contradictory anchor/tempo information is warned
  about, not used to invent a new clock.
- HOPO/tap/open/sustain/phrase gameplay is not implemented. D-pad checks cover
  simultaneous onsets; held-sustain overlaps and ergonomics need later validation.
- Audio licensing, recording/version matching and preparation need authorization;
  no compression, muting or guitar-volume features have been implemented.
- Music still loops without resetting demo notes. Physical hardware testing,
  manual listening/play, latency measurement and multi-hour runs remain outstanding.
- Baseline code/music/art redistribution permissions are not newly established.
  Source credits remain; ignored input/output folders avoid accidental community
  chart redistribution.

## Recommended Mission 004 sequence

1. Obtain a properly authorized chart and matching recording, or continue with
   synthetic data until those are available. Keep source/author/license/version.
2. Review the import report and required lane layouts without silently remapping.
3. Design and test the absolute-time game/audio adapter, retaining a verified
   legacy demo path or measuring any proposed recalibration explicitly.
4. Implement only the approved difficulty renderer/integration next. Do not add
   reactive audio penalties or new assets just because import preparation passed.
5. Later, existing judgment events can drive an authorized reactive-audio task.

PR creation previously failed with GitHub API Forbidden while Git pushes worked.
The final handoff reports the new attempt separately; a source branch or compare
link must not be described as an opened pull request. Download branches remain
separate and must not be merged into main.
