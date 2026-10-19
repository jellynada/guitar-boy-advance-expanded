# Mission 005 — actual results

## Starting point and scope

Source base:Mission004 `1487532557a1e98b1c99c6628e5d65c291268cd2`, containing
Missions001–004 by inspected ancestry. Branch `mission-005-first-playable-import`.
Remote main remains original `6c4e63460fab10733d8ff011045ee246e7201952`.
No automatic merge. New runtime is deliberately an optional silent Easy test.

Original NoteManager, NoteJudgment, chart, music and art source files are unchanged.
Main/sprite integration adds mode dispatch and clean state reset. Existing Mode7
projection source is unchanged; imported mode derives a three-stripe floor and
places three fret buttons, restoring original data when switching back. Original
manager now has static storage, with no new heap allocation or per-frame allocation.
The ROM differs from Mission004 because the selector, adapter, fixture, shared
mode reset/rendering and storage initialization change the linked program.

## Real private package findings

The owner supplied the actual `Cream (WaveGroup) - Sunshine of Your Love (Neversoft).zip`.
Mission004 importer ran successfully against it in this workspace, without audio
decoding. MIDI PPQ480,329tempo points, one meter. Lead guitar:

| Difficulty | Notes | Native frets | Chords | Proposed D-pad onset conflicts |
| --- | ---: | --- | ---: | ---: |
| Easy | 395 | 0,1,2 | 0 | 0 |
| Medium | 686 | 0,1,2,3 | 185 | 11 |
| Hard | 878 | 0,1,2,3,4 | 279 | 20 |
| Expert | 998 | 0,1,2,3,4 | 294 | No approved mapping |

Bass is also detected. Audio filenames:guitar.opus,rhythm.opus,song.opus,
preview.opus; preview excluded from future gameplay-stem selection. Title/artist
identify Cream(WaveGroup), and INI tags identify a cover. No recording playback
or audible alignment is claimed.

Easy preparation preserved every395note and mapped native0/1/2→Left/A/B.
At explicit ceil(PPQ/3)=160tick test threshold,317short releases and78genuine
sustains,0native same-lane sustained overlaps. Maximum simultaneous visible
notes4/32. The source's sustain_cutoff_threshold=0 is retained and explicitly
reported as overridden for test classification only; no raw duration is changed.
First onset4.322s, last262.880s, plus2s pre-roll at runtime. Extra timing offset0.

Only factual aggregate findings are recorded here. ZIP, chart events, normalized
source, adapted private note/header files, audio and private chart-ROM stay outside
tracked/public source. Public fixtures/bundle include synthetic data only.

## Host tests actually run

`bash tests/check.sh` passed under Python3.12.14/host GCC14.2:

- 32 existing chart-importer tests, including actual desktop and ARM7TDMI/Thumb
 header compilation with devkitARM on PATH; no skipped tests.
- 34 existing MIDI/package importer tests.
- 9 new adaptation tests: independent first/boundary/final timestamps, native/source
 preservation, explicit selection/lane bounds, malformed/overflowing/duplicate/
 unordered data, sustain cutoff/overlap, sprite density rejection, deterministic
 output, CLI invalid cleanup and one-command package→Easy preparation.
- Existing ASan/UBSan/leak judgment and full699-note tests passed unchanged.
- New ASan/UBSan/leak imported runtime test: exact cycle conversion, one-hour
 references, frame-rounding bound, three/four-lane mapping, normal/held/repeated
 hit behavior, automatic misses through skipped frames, first/final safety,
 monotonic stale reads, repeated reset, bounded projection coordinates and final
 late-window handling at the maximum chart duration.

**75Python tests passed**, plus the C++ sanitizer/test programs. No failure or
skip is reported as a pass. Source package/adaptation outputs remain ignored.

## Real builds actually performed

Native build with prepared devkitARM and `make -j2`; clean Docker build with:

```bash
bash scripts/build-docker.sh clean
bash scripts/build-docker.sh
```

Public synthetic ROM:`guitar-boy-advance-expanded.gba`,278780bytes, SHA256:

```text
ddd51770e8f8c037df3cc66bf128f49f777e49638c3d4f1de7a0d0dbd8252883
```

Native and pinned Docker outputs match. The public download copy is
`guitar-boy-advance-mission-005.gba`. The existing pinned toolchain digest remains
unchanged; Python3 is available in that image. Native Make uses its source folder basename for the output filename; the Docker
helper mounts a fixed folder name so its output is always guitar-boy-advance-expanded.gba.

An explicit private build used:

```bash
python3 tools/prepare_easy.py "<owner's ZIP>"
make -j2 IMPORTED_HEADER=imports/output/easy-runtime/imported_chart.hpp
```

Private chart-ROM:284868bytes, built and retained privately, not published.
No Cream audio is embedded. Default build afterward was verified to restore the
public synthetic selection. Linked original699 `<QII>` Note records were read
from the public ROM and independently matched the original chart and legacy
conversion exactly. Existing16-byte layout/alignment checks pass.

## Actual mGBA0.10.1 gameplay tests

| ROM/mode | Frames per run | Perfect | Good | Miss | Wrong |
| --- | ---: | ---: | ---: | ---: | ---: |
| Public original, all-hit | 36000 | 699 | 0 | 0 | 0 |
| Public original, no-input | 36000 | 0 | 0 | 699 | 0 |
| Public original, mixed | 36000 | 72 | 105 | 522 | 1200 |
| Public synthetic Easy, all-hit | 1800 | 25 | 0 | 0 | 0 |
| Public synthetic Easy, no-input | 1800 | 0 | 0 | 25 | 0 |
| Private real Easy, all-hit | 18000 | 395 | 0 | 0 | 0 |
| Private real Easy, no-input | 18000 | 0 | 0 | 395 | 0 |

No core crashes. Original runs include changing framebuffer, nonzero audio and
visible hit-tile feedback. Mixed totals differ from older mission logs because
the scripted input now starts after selector confirmation, changing its phase;
no judgment formulas/windows changed. Every run counts each note once.

Imported runs check bounded visibility cursors, actual projected note OAM,
correct physical Left/A/B input, Right ignored, and **zero nonzero audio samples**.
Each imported scenario also returns to the selector and switches original→imported
three times, checks fresh counters/clock and checks original audio resumes then
imported output returns to silence. Frontend buffered samples are drained before
post-switch steady-silence measurement; no instantaneous zero-tail claim is made.

Synthetic selector and three-lane gameplay screenshots were visually inspected:
three stripes/fret circles, aligned perspective notes, label and hit/miss HUD.
The public screenshot may show missed notes because the no-input test captures it.
No human keyboard/controller playthrough, manual listening, physical GBA run or
latency calibration was performed.

## Timing measurements and meaning

Frame time280896/16777216=16.7427063ms. New canonical timestamp→cycle rounding
adds at most0.000029803ms, and prior integer-microsecond normalization adds at most
0.0005ms. Frame sampling dominates; no repeated millisecond/frame rounding drifts
with song length. Synthetic reference-frame tests measured max11.405945ms across
beginning/middle/end and a one-hour endpoint. Emulator scheduled-hit max errors:
synthetic16.700745ms, real16.694248ms, within one hardware frame.

These demonstrate monotonic chart timing and frame-based judgment, **not audio
synchronization**. A future sample-position clock and measured output latency must
replace or align this silent test clock before claiming recording sync.

## Remaining work and review

Silent onset play only: no new audio decoding, compression, mixing, sustain/HOPO/
tap gameplay, scores, imported Medium/Hard, new libraries or full song menu.
Windows11 guide and local private-build commands:GBA_CHART_ADAPTATION.md.
Next:authorized synthetic audio/sample-clock proof and CPU/memory/latency budget,
then matching-cover calibration before reactive audio.

Review base `mission-004-universal-import`, head `mission-005-first-playable-import`.
No automatic merge. Public download branch must remain separate. Actual PR
creation outcome is recorded below after the attempt; a compare link is not a PR.
