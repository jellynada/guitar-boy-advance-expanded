# Arcade75 verification record

Frozen source: `6c627e36dc30286575183c10076258d0bc9a7a0a`.
Engine under test: `61e4de93e29f09fede3d3e994c76a7f030ca3c3b`.
Final documentation/test-only source revision is recorded in build manifests.
Final ROMs must match this engine outside the 40-byte revision marker, and
extracted packages are checked again. Only the new working branch is pushed;
no merge, stable release or handheld acceptance is implied.

## Native preservation and exact changes

Original Cream Easy/Medium/Hard remain 395/78, 686/172 and 878/175 heads/holds.
Native normalized JSON and both original source streams remain untouched.
Public and full-native engine binaries match stabilization outside revision.
The old 37 behavior/input cases pass; original observers/thresholds are unchanged.
Full native-All passes all 12 difficulty/pause/completion cases. Its Easy short
pause trace retains 15,815 points. The unchanged original 699-note demo passes
Perfect, miss and mixed inputs. Public physical/label and graphics checks pass.

Apply the source-time cut first, then validate/adapt:

| Chart | Kept heads | Kept holds | Excluded heads | Opposing events | Shifted | Deleted |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Easy | 110 | 20 | 285 | 0 | 0 | 0 |
| Medium | 186 | 38 | 500 | 3 | 3 | 0 |
| Hard | 235 | 39 | 643 | 4 | 4 | 0 |

Exact source-time lane changes (IDs are zero-based original track indices):

| Chart | Source ID | Source time | Original lane/button | Derived lane/button |
| --- | ---: | ---: | --- | --- |
| Medium | 137 | 57.992s | 1 RIGHT | 2 B |
| Medium | 147 | 62.152s | 1 RIGHT | 2 B |
| Medium | 157 | 66.390s | 1 RIGHT | 2 B |
| Hard | 169 | 57.992s | 0 LEFT | 1 UP/DOWN |
| Hard | 179 | 62.152s | 0 LEFT | 1 UP/DOWN |
| Hard | 187 | 65.328s | 0 LEFT | 1 UP/DOWN |
| Hard | 190 | 66.390s | 0 LEFT | 1 UP/DOWN |

No remaining opposing interval conflicts or new same-lane collisions. Every
other retained lane/onset stays native. The impossible Hard triple retains
three heads through reassignment; playable triples remain untouched. Original
synthetic Easy LEFT+B+A triples at 12/20/30s remain intact. The public exercise
also forces the legitimate fallback: Medium/Hard each remove two heads from
fully occupied impossible chords, with associated holds cleanly removed.

Private `derivation-report.json` includes all original IDs/ticks and final records,
including excluded notes/tail clipping. Source history contains analytical
summaries only. `measurements.json` includes clipped-tail identities/end times.
Repeated real Cream preparation produces identical manifests and every output
hash. Normalized native JSON is byte-identical to full-length preparation.

## Audio duration and scoring

Each stem: exactly 1,228,800 source samples (75s), plus 32,768 count-in samples;
1,261,568 played samples (77s including count-in), zero added playback tail.
The final 1,228 source samples share a 74.951ms deterministic fade ending at zero.
Both un-faded prefixes match full-length PCM byte-for-byte. Source offsets,
codec pre-skip and role alignment are retained. Last-sample-clock clipping is
documented in ARCADE_CUT_75_V1.md. Full/native preparation retains old padding.

On-time full-hold score references: Easy 3923, Medium 7060, Hard 9029. These use
the unchanged score formula and prepared counts. Actual uninterrupted host key
traces give 3919/7052/9013, respectively, all Perfect and all holds completed.
Inherited sub-frame hit timing affects hold-bonus boundaries; these are separate
references, not errors forced to the old full-length 15,815 total. Every smoke
case asserts score/head/coherence/completion under the existing core rules.

Three unmodified-ROM short digital captures (Perfect, all-miss, mixed) each
verify 1,261,568 consumed samples and 315,388 mixer words with zero mismatches;
FIFO request periods 1022–1026 cycles, complete clock drift zero. The explicit
inherited 15-sample silent startup advance is unchanged, never fitted per window.
All three ordinary output comparisons and mixed common-backing/mute/recovery
comparison pass at the established thresholds, using valid full windows at
6.322/37.5/76.7 runtime seconds. An initial 76.9s request extended its comparison
window past EOF and was rejected; no threshold/window-size change was made.

Full-length ordinary output is still **10/15 pass, 5 fail**, exactly the known
stabilization pattern (scoring/reactive primary; scoring/wrong/reactive strict
backing). The byte-identical full-length game/audio and freshly repeated full
captures retain that characterization. No emulator source patch, diagnostic
lateness correction, extra phase padding or relaxed threshold is used. Passing
short captures does not resolve the inherited output-stage/hardware-listening
gate. Digital and output records are stored separately.

## Performance, memory and capacity

Same derived charts/PCM are run on an isolated frozen stabilization engine and
the candidate. Only host audio validation helpers in the isolated baseline
snapshot accept cut metadata; its game source is frozen and it is not shipped.

| Chart | Frozen same-assets peak | Candidate graphics peak | Highest candidate smoke peak |
| --- | ---: | ---: | ---: |
| Easy | 133056 | 133056 | 133120 |
| Medium | 222400 | 222400 | 223232 |
| Hard | 248640 | 248768 | 248896 |

Hard same-assets mean: 106351→106445 cycles (+94 cycles, ~0.089%). No per-frame
adaptation or audio trimming exists. The small finite-EOF guard is the only new
runtime path, closing late misses and newly activated clipped holds at the same
final tick. Worst observed candidate 248896 leaves 32000 cycles (11.39%) of the
280896-cycle frame. This is measured workload evidence, not a universal bound.

Each difficulty's full cut graphics run has 4570 eligible highway scans with
zero displaced pixels. Peak sustain strips: 10/20/27; no tail overflow. Refill
IRQ peak 1408 cycles; scanline re-arm peak 2048 cycles, latest VCOUNT162, zero
misses. Audio underruns zero. Hard mixed/pause stress peak 245824 cycles; stack
canary observes 940 user bytes touched with 4464 untouched, IRQ 40 of 160 bytes.
These are observed stack margins, not maximum-stack proofs for every input.

Cut ROM: 2,878,020 bytes; native-All full ROM: 9,229,228 bytes at engine check.
Each cut stem stores 1,277,952 bytes including count-in/guard/alignment, total
2,555,904 bytes. Source music alone: 2,457,600 bytes. Prepared header text:
22,877 bytes; 531 heads times 16-byte Note + 8-byte hold = 12,744 runtime array
bytes, plus choices/labels/alignment. Compiler section measurements retain
IWRAM/EWRAM static footprints; no new runtime data allocator or library exists.

Ten similar cuts with current padding require 25,559,040 audio bytes. Reserve
1MiB for shared engine/graphics, 1MiB for charts/metadata, 64KiB alignment and
2MiB safety margin: total 29,818,880 bytes, leaving 3,735,552 bytes within 32MiB.
This conservative forecast includes margin; it does not implement song storage,
prove arbitrary chart lengths fit or establish runtime multi-song playability.

## Regression and delivery

Host suite: 165 existing + 28 new Python tests, 12 existing + 1 new ASan/UBSan
programs. The complete existing suite passes; dedicated tests include public
allowlist rejection and finite-EOF short-hold settlement. Real Cream75 and the
original synthetic Arcade75 exercise each pass 12/12 actual-key difficulty
smokes. All three Cream difficulties also pass a two-second pause just before
EOF. Full native-All and original demo tests are retained separately.

Failure history is preserved: parallel Docker builds exhausted temporary disk
space (original files intact; subsequent builds serialized); initial old error
message/test include regressions were corrected; strict final-hold validation
caught last-sample clipping, and the intentional synthetic near-EOF hold exposed
missing final hold settlement. Neither regression assertion was weakened.

Final packages are built from clean committed source, verified against tested
ROM hashes, extracted and emulated. The existing synthetic review ZIP remains
separate. The additional public Arcade75 ZIP is authorized only after exact
independent regeneration of the original fixture; generic owner input remains
private. CI confirms its own run/artifact; network downloading must be reported
separately from local CRC/hash/extraction tests. Local paths are not download links.

Real Cream native-All + Arcade75 are packaged locally as AES-256 ZIP, with a fresh
strong password stored separately and independent 7-Zip test/extraction. No
private upload capability is configured, so owner transfer remains blocked.
No encrypted recording is placed in public source history. The Windows launcher
is unchanged. Final manifests/receipts record exact hashes and source revisions.

Next owner gate: receive the exact private candidate through an authorized route,
then follow OWNER_ARCADE75_PLAYTEST.md on a real GBA. Confirm rewritten chords,
diagonals/alias handoff, holds, muting/recovery, pause near EOF, results/replay,
graphics and audio synchronization. Review the inherited full-length audio issue
explicitly before integration. No acceptance, merge, stable release, multi-song
mission or additional feature work is authorized by these emulator results.
