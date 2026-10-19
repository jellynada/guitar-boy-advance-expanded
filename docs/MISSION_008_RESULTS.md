# Mission 008 results and handoff

Base:verified Mission007 `90aaed9f2d7624258ff3485d6a0dc7858c126929`, containing
Missions001–007. Source branch:mission-008-scoring-results. Main is not merged.
Public imported content is original synthetic material; the new private Cream
recording/chart/ROM/full traces are not committed or included in public bundles.

## Implementation and preserved systems

Independent fixed-storage NoteScore consumes existing judgment events and protects
chart identities with one bit per note. Perfect10/Good5base, combo-before-award,
thresholds10/20/30 for2x/3x/4x, no extra bonuses. Miss/WrongInput reset combo;
maximum combo/highest multiplier persist. Integer accuracy uses successful notes
out of selected chart notes. FC/AP require finalized nonempty sessions without
wrong inputs. Saturating32bit score/wrong arithmetic prevents wrap.

Imported HUD uses existing8x8font on two BG0rows above the highway. It fits
10digit score/combo values and retains the existing BG1 black depth mask and
blend behavior. Results use BG1 after playback end and coherent resolution,
with A/Start replay or B/Select selection. New error states clearly show partial
statistics without awards. Silence fallback has a tested explicit deadline.
Sanitized bounded title metadata is added to generated headers; note timing/data
are preserved. Old caches should be regenerated with the documented preparation.

NoteJudgment, NoteManager, imported projection/clock, reactive gate and PCM mixer
sources are unchanged. Private prepared guitar/backing PCM is byte-identical to
Mission007. Scoring never controls volume, playback position, chart timing or
which notes hit. Original Demo retains its original flow and H/M feedback;
no scoring/results retrofit was attempted for that mode.

## Performed host tests

`bash tests/check.sh`:93Python tests (32chart,34MIDI/package,10adaptation,12audio,
5reactive), plus sanitizer-backed C++ judgment,699-note chart, imported runtime,
clock, gate and scoring/session checks. No GBA-compiler-dependent tests skipped.

Scoring tests cover each Perfect/Good threshold, base points,4xcap, reset/max
retention, duplicates/out-of-range identities, actual engine chord/held/repeated
press events, same-update miss→hit and hit→wrong order with gate agreement,
8192-note score bounds, saturating addition, reset/finalization, fixed-point
accuracy, zero-note fixtures, FC/AP, end/fault/inconsistency/silent completion, including an end-interrupt/stale-snapshot race guard.
A separate bucket calculation confirms9*10+10*20+10*30+366*40=15230 for395notes.
Title tests cover escaping, ASCII/length bounds and unchanged note arrays.

## Complete automated mGBA tests

Public synthetic runs:1800frames per complete scenario. Private Cream:
18000frames per scenario, covering the full267.271912s recording,2s pre-roll,
0.5s playback tail, EOF and results. Each normal scenario waits on results,
asserts score stays fixed, tests replay, then four original/imported mode cycles.
Additional public B/Select results tests return to selection and start afresh.

| Scenario | Public judgments and score | Private Cream judgments and score |
| --- | --- | --- |
| All Perfect | 25P,470 | 395P,15230 |
| All Good | 25G,235 | 395G,7615 |
| No input | 25Miss,0 | 395Miss,0 |
| Hit/miss/hit | 17P/8Miss,170 | 263P/132Miss,2630 |
| Mixed timing | 13P/6G/6Miss,160 | 197P/99G/99Miss,2465 |
| Wrong presses + hits | 25P/29Wrong,250 | 375P/20G/565Wrong,3850 |

Private all-Perfect results:15230score,395combo/max,4xhighest,395Perfect,
0Good/Miss/Wrong,100.00%, FC=yes, AP=yes. All-Good:7615,395combo/max,4x,
100.00%, FC=yes, AP=no. Wrong-input run:100.00%note accuracy, FC/AP=no. Mixed
timing:74.94%, maximum3, highest1x; resets are deliberate in that input script.
The trace-based independent tally agrees with runtime score/combo/max/multiplier
throughout each reactive run, rather than only checking the last screen.

Wrong-input totals are lower than Mission007's long capture scripts because
Mission008 stops judging at EOF/results; extra post-EOF presses no longer count.
Events before completion retain the established judgment semantics.

Results tilemaps were read directly from actual GBA VRAM and checked against
final score, accuracy, each count, maximum/highest multiplier, awards, completion
or error status and both control prompts. Screenshots were inspected for public
HUD/results readability and retained highway appearance. This is automated
emulation/visual inspection, not manual playing or human listening.

Original Demo:36000frames each. All-hit699Perfect; no-input699Miss; mixed59P,
118Good,522Miss,1200Wrong. Every note counted once, original sound and hit-tile
feedback present, no core crash. These match the established baseline patterns.

Public fault cases disable sample timer, refill timer, sound, refill IRQ or block
IRQs for one frame. They end in AudioError, freeze stats/clock, show partial
results and award neither FC nor AP. Injected missed refills increment the
underrun counter. No normal scenario reports an underrun. Debugger injection now
waits outside ISR execution so the saved IME/IE restoration cannot undo it.
A forced premature EOF with pending notes produces Inconsistent/DATA ERROR,
stops sound and never claims completion. No notes are fabricated as successes.

Silent fallback is tested both no-input and all-Perfect through results/replay:
25Miss/0points or25Perfect/470points, zero imported audio, correct awards.
The fixed-mix compatibility check runs1000frames and four replay/mode cycles;
its entire recording was not rerun. Its continuous full mix remains nonreactive.

## Captured audio and synchronization

Actual mGBA signed16 output at32768Hz is compared to independently calculated
sample mixes/fades from real event positions. Both streams use the unchanged
shared16384Hz timer and cursor. Checks cover normal sound, true-zero source gate,
expected backing-only output, recovery, fade edges, beginning/middle/end and EOF.
All six public/private scenarios pass. Private hit/miss pattern has131recoveries;
the mixed timing pattern has98. No captured clipping; final post-EOF second is
silent. General nonzero audio is not treated as proof of correct backing.

Primary prepared-PCM/model checks pass with the unchanged analyzer thresholds,
including the fitted guitar contribution bound during muted regions. An optional
cross-run comparison against another actual no-input capture missed its stricter
0.999correlation threshold at a short wrong-input window (0.99519; backing scale
0.99629; residual fitted guitar0.165%). Cross-run sample identity is not claimed.
Local hardware/capture mapping and fixed global epoch residuals are reported
separately without in-game latency compensation. Exact per-window private data
remain local; final correlation minima are recorded below. This is emulator-model evidence with filtering,
quantization and capture uncertainty, not proof of analog silence or physical
hardware timing. Owner Mission007 sound/feel approval is retained as feedback,
not claimed as a new Mission008 manual test.

First/middle/final note OAM positions cross the fret line within one16.742706ms
frame. Miss-run REFERENCE timestamps are late judgments, not contact errors.
Final measured timings, storage and resource figures follow below.

## Build and delivery

Native devkitARM r68/GCC16.1.0, Tonc1.4.5, MaxmodGBA1.0.15; host Python3.12.14,
FFmpeg7.1.5; automated mGBA0.10.1. Existing pinned Docker workflow is unchanged:
`devkitpro/devkitarm@sha256:116afba8df8453961de2936ffab20dd441edf4d682856c1ec8b0e53d7ed0bbf5`.
No new dependencies or art. NumPy remains optional for developer waveform analysis.
Windows installation and physical hardware were not tested in this environment.

Source and public downloads use separate branches; neither merges to main.
The public ROM and full source/review bundle contain the original25-note
synthetic fixture. They exclude Cream files, prepared streams, private ROM,
full chart/event traces and private captured sound. Only aggregate private
findings and requested reference measurements are included.

Private build is saved at
`/workspace/.cloud-setup/gba/mission008-private-rom/guitar-boy-advance-expanded.gba`,
also copied to `/workspace/artifacts/Sunshine-of-Your-Love-Mission-008-Private.gba`.
This session has no working private attachment/export tool. These paths are not
download links. SCORING_AND_RESULTS.md gives exact Windows11/WSL/Docker commands
using the owner's existing ZIP. No new private content is publicly uploaded.

No score saving, original-mode results, sustain scoring, new difficulties,
codec changes, health, stars or full song menus. Next:owner playtest of HUD,
results/replay/error feedback, physical hardware, then focused Mission009 scope.


## Final measured artifacts

| Build | ROM bytes | IWRAM sections | EWRAM sections |
| --- | ---: | ---: | ---: |
| public | 801972 | 26028 | 2912 |
| private | 9161952 | 26444 | 2912 |

RAM excludes stack/BIOS reservations. IWRAM rises132bytes/public and180/private
above Mission007; EWRAM is unchanged. HUD/results reuse existing glyph data with
6144bytes of unused character VRAM for two copies; no new art or per-frame heap.
Stack high-water and physical performance were not measured.

Public SHA256:

```
96ec67ef3f8705e3ffd0d5390cad8fd2f5df5bcae2c166cb88e69775ce512e81
```

Private SHA256:

```
2b5762ccbaf3799aeb64bea14693a7b84ae72ae4681cf72e68f5d9b4adfc487d
```

Both aligned PCM blobs and the original699-note binary were verified in each
linked ROM. All395adapted private notes/timings and private guitar/backing PCM
match Mission007. No codec, rate, fade or mix changes.

| Reference | Expected runtime | Note-line absolute error | Waveform/local-clock residual |
| --- | ---: | ---: | ---: |
| Public first | 2.000000s | 2.563ms | -0.641ms |
| Public middle | 9.333333s | 2.666ms | -0.641ms |
| Public final | 13.333333s | 4.069ms | -0.702ms |
| Private first | 6.322000s | 0.082ms | -0.610ms |
| Private middle | 139.434000s | 9.481ms | -0.610ms |
| Private final | 264.880000s | 0.005ms | -0.671ms |

One frame is16.742706ms. OAM crossings measure draw snapshots, not physical
scanout/host presentation. Local waveform mapping uses independent hardware
timestamps; fixed-epoch residuals remain in analysis output. No new calibration
offset or independent stem clock. Final results freeze at the final audio tick.

Work excludes idle waiting. Foreground intervals include overlapping IRQ work;
refill measurements exclude dispatcher entry/exit. They must not be added as
independent CPU percentages. Timer3 resolution is64CPUcycles.

| Build/run | Foreground mean cycles (%frame) | Foreground max cycles | Refill mean cycles | Refill max cycles |
| --- | ---: | ---: | ---: | ---: |
| public/perfect | 87932.2 (31.30%) | 113344 | 1342.6 | 1344 |
| public/good | 87895.2 (31.29%) | 113280 | 1342.5 | 1344 |
| public/miss | 87799.3 (31.26%) | 105792 | 1357.8 | 1472 |
| public/reactive | 87828.1 (31.27%) | 112512 | 1347.0 | 1472 |
| public/wrong | 88779.0 (31.61%) | 112704 | 1356.4 | 1472 |
| public/scoring | 87820.6 (31.26%) | 112000 | 1345.3 | 1472 |
| private/perfect | 87341.0 (31.09%) | 114112 | 1342.5 | 1344 |
| private/good | 87310.8 (31.08%) | 118144 | 1342.5 | 1344 |
| private/miss | 87068.2 (31.00%) | 106496 | 1354.5 | 1408 |
| private/reactive | 87203.4 (31.04%) | 110784 | 1346.4 | 1472 |
| private/wrong | 88372.6 (31.46%) | 114880 | 1351.3 | 1472 |
| private/scoring | 87195.4 (31.04%) | 114496 | 1345.2 | 1472 |

Worst refill1472cycles remains below the16384cycle interval. No normal-run
underruns or captured clipping. These are emulator measurements; full physical
CPU/interrupt/bus costs remain unverified.
