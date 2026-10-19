# Mission 011 — audio/graphics timing stabilization

**Outcome B — partial repair; review candidate, stable promotion blocked.**
The imported highway repair passes the full-song composed-frame regression.
All eight ordinary primary real waveform models pass, but two additional strict
ordinary-emulator backing comparisons still fail. Their emulator timing cause is
established by controlled correction experiments; that correction is not shipped
in the game or silently enabled for normal tests. Owner Windows/hardware acceptance
and emulator compatibility validation remain outstanding. No music/gameplay rules
or test acceptance thresholds were changed.

## Verified starting point and diagnostic phase

Remote `mission-010-stabilization` was fetched and verified at
`233112a072e5a0e90e5a766207761474130f75a6`; main remained
`6c4e63460fab10733d8ff011045ee246e7201952`. Hotfix71f0152,
sustains85c637d, diagnostics1d92104, framebuffer53a6134 and build guard3b0ce46
are verified ancestors. New source branch: mission-011-audio-graphics-stability.
No download branch, merge, force push, main change or new gameplay feature.

Pre-change host suite:98Python tests and8C++ sanitizer programs pass. A fresh
full395-note mixed reactive run reproduces exactly the M010 failure at232.665039s:
correlation0.9099746798974478, threshold>0.94, residual-0.67138671875ms.
Seven primary waveform models and gameplay results previously passed; one stricter
optional common-backing comparison also failed at46.137634s. No thresholds have
been changed during the diagnostic phase.

Rollback ROMs, built with ARM GCC16.1.0 /pinned official Docker image:

- M010synthetic814980bytes, SHA256
  `48ff797804e86e59f70b4e733d5af651616a75b3d9dbe6bc1bb0026c1e6790ac`.
- M010Cream9178392bytes, SHA256
  `c48ca749df60522402cc77204e5100c1f3c7121244c97f2df8539892f62b8c5d`.
- Real max foreground170560cycles/frame; typical run means99995.5–104720.5.
  Public max233728. Reactive refill maximum1472; zero ordinary underruns.
  Linked IWRAM27076real/26660synthetic; EWRAM3464/3096 plus padding.
  Tail strips11real/31synthetic in full regressions. Physical hardware untested.

## Observation without changing emulated execution

`tests/hardware_tap.c` interposes the installed mGBA0.10.1 host functions. It
observes actual FIFO words, consumed signed8 samples, pre-resampler PWM samples,
scanline-register writes and their emulated timestamps. No GBA instructions or
CPU-cycle delays are added. The full tapped M010 reactive capture is byte-identical
to the untapped fresh capture; this is an explicit observer-effect check. It uses
mGBA private headers and is version-specific; it is not linked into the ROM.
Earlier M010 in-ROM instrumentation had nonzero observer overhead; it is not used
as the quantitative controlled comparison here.

In the fresh baseline,1,104,984observed four-byte FIFO writes match an independent
source+event/gain model exactly. All4,419,952observed consumed samples match the
model after a fixed15sample advance, with zero sample mismatches. This distinguishes
digital PCM correctness from PWM/resampler output; it does not yet declare the
waveform regression solved. Startup priming and emulator FIFO details are being
investigated separately; no arbitrary audio offset is added to the game.

## Controlled graphics experiment design

`tests/run_timing_matrix.py` exports a pinned source revision, uses one compiler
and checks each build before saving its matching ROM/ELF. Artificial combinations
are developer-only. It generates original tones/zeros with the real267.271912s
sample count, identical pre-roll/tail/guard and two equally-sized PCM streams;
manifest hashes bind the selected chart. None is a playable replacement song.

Cases: original Maxmod demo; short synthetic chart/audio; same chart silent;
real chart/real audio; real chart/long synthetic tones; synthetic chart/long tones;
synthetic chart/long zero streams; real chart/audio with only tail drawing omitted.
The tail experiment preserves judgments and hold logic.1800frames per case include
four60-frame consecutive native sequences. Normal gameplay runs retain tails.

The host framebuffer oracle projects the real affine texture/map/palette and
counts actual highway-colored pixels outside their expected floor locations.
It includes existing15/16floor blending (Tonc clamp's upper bound is exclusive),
requires actual highway pixels, and is not a black-mask/screenshot similarity test.
It can also expose foreground table/scanout races; the silent baseline has five
flagged frames without late IRQ writes. That uncertainty is retained rather than
calling every pixel difference an IRQ artifact. Original Demo's different texture
is assessed by actual sequences and register-write timing, not this imported oracle.

Provisional controlled observations: real/tones/zeros all reproduce displaced
floor lines; omitting tails does not remove them. Thus Cream's recording content
is not required. Short synthetic also has measurable defects despite appearing
clean to the owner, while Original's normal music has no recurrent software FIFO
refill IRQ and no late affine writes in this comparison. Long test streams keep
exercising the fault after the short public song has already ended. These results
explain opportunity/architecture differences; they do not prove the owner's exact
photograph or perceived severity has been reproduced on Windows.

## IRQ and resource audit before selecting a repair

The linked Tonc `isr_master` acknowledges all simultaneously pending flags, selects
one callback by table priority, masks interrupts and leaves IME off during that
callback. Timer1 was inserted at priority0; HBlank is later. Simultaneous requests
can therefore lose a graphics callback, and running FIFO work can delay another.
The1344–1472cycle refill exceeds a1232cycle scanline and far exceeds272cycle HBlank.
A missed perspective reference write also leaves the old PB/PD increment behavior
active, producing displaced rather than simply dimmer floor pixels. Foreground
rewrites of the table during scanout are an additional smaller race to eliminate.

Imported audio owns Timers0–2 and FIFO A, and stops DMA1/2; original Maxmod uses
DMA1/2. No application code owns DMA0/3. Tonc sprite/memory copies and BIOS LZ77
are CPU operations here. Candidate: imported-only, double-buffered affine/fog
scanline tables using DMA0/3, rearmed in VBlank and stopped before scene changes.
Original renderer/Maxmod remain on their established path. This avoids introducing
nested IRQ stack/reentrancy changes throughout the game. Shortening the mixer
alone cannot prove every HBlank deadline, particularly with simultaneous flag loss.
Implementation and final measured results will follow only after validation.

## Implemented graphics repair

Implementation commit: `d0b20dc`; focused QA/oracle commit: `bb6f378`.
`source/scanline.cpp` transports the **existing** perspective and fog data using
DMA0 (four affine words) and DMA3 (one blend halfword). Two161-entry frames use
5800bytes EWRAM, including the safe sentinel transfer after visible line159.
The producer fills only an inactive frame, publishes it after a compiler barrier,
and never edits the table currently being scanned. Above-horizon entries are
initialized and use the existing fully opaque depth-mask state. Existing lane
geometry, art, fog coefficients (including maximum15), heads/tails and HUD remain.
No crop, black rectangle, disabled tails, animation or lower-quality highway is
used to conceal the fault.

DMA is rearmed by foreground code immediately after the existing hardware-polled
`vid_vsync()`, not a VBlank callback that Tonc can discard alongside Timer1.
Counters check entry while VBlank is active; observed latest entry is line162,
maximum rearm interval2048cycles, zero deadline misses. All channels are stopped
before results, mode selection, diagnostics and original Maxmod initialization.
Original Demo retains its CPU scanline/Maxmod path. DMA1/2, PCM/refill/gain logic,
judgment windows, score and sustain policy are unchanged.

The alternative of changing to nested interrupt dispatch was rejected because it
would alter stack/preemption assumptions for all callbacks and original Maxmod.
Shortening the mixer alone would not address acknowledged/discarded graphics IRQs
or the table/scanout race. The bounded transport isolates the change to imported
rendering and preserves the original projection computation.

## Controlled before/after results

Same pinned compiler; source M010233112a versus M011d0b20dc. The synthetic row
below uses the corrected framebuffer oracle in a fresh baseline run; an earlier
provisional run with an incorrect palette/blend assumption counted zero floor
pixels and is **not** accepted as visual evidence.

| Case /1800frames | Before flagged frames | After flagged frames | Before late X writes | After late X writes |
| --- | ---: | ---: | ---: | ---: |
| Short synthetic chart/audio | 856/857 | 0/857 | 7515 | 0 |
| Same chart, silent | 5/773 | 0/773 | 0 | 0 |
| Cream chart /actual Cream audio | 1769/1769 | 0/1769 | 15250 | 0 |
| Cream chart /long original tones | 1769/1769 | 0/1769 | 15250 | 0 |
| Synthetic chart /equally long tones | 1769/1769 | 0/1769 | 15267 | 0 |
| Synthetic chart /equally long zero PCM | 1769/1769 | 0/1769 | 15267 | 0 |
| Cream, only tail drawing omitted | 1769/1769 | 0/1769 | 15242 | 0 |
| Original Demo /normal Maxmod | Imported oracle not applicable | Native sequences checked | 0 | 0 |

Denominators count actual gameplay frames after31warmup frames; short/silent
sessions have already reached results before1800frames. They do not measure
owner-perceived severity. The silent five-frame discrepancy can include the old
foreground table/scanout race, independently of audio IRQ lateness. Both races are
removed by publishing complete scanline tables; no claim all graphical defects
are solved.

Full real-song comparison,16400frames each: before16085/16085gameplay frames
flagged,966167displaced pixels total, worst303per frame; after0/16086flagged,
zero displaced pixels,184676819visible floor pixels checked. The one-frame count
difference comes from scene-initialization timing. No new blackout or hidden floor.
A second full run checks2,578,320X writes,2,578,320final affine-word writes and
2,578,320blend writes: **zero outside HBlank**. The minimum observed remaining
HBlank interval at a final-word/blend write is13emulated cycles. This is a
measured simulator margin, not a physical-hardware deadline guarantee.

Consecutive60-frame sequences are captured around script frames180,420,900,1500,
4800,9000,15000,15800when those frames exist. All full Cream sequences remain
private. Public before/after sequences use original synthetic content and native
240x160pixels. APNG previews use17ms/frame; individual PNGs retain source pixels.
The delivered browser comparison enlarges them only for viewing, without editing
the screenshot data. Full-song framebuffer checks run every eligible frame,
not only the illustrated excerpts.

### Why Cream appeared worse to the owner

The verified cause is not decoding Cream, its musical samples, larger PCM values,
or genuine hold drawing: replacement tones/zeros and omitted tails retain the
old fault. Original's DMA-based Maxmod path lacks the frequent CPU FIFO refill
interrupt that conflicts with the CPU scanline handler. The short synthetic mode
also has measurable displaced lines, despite no noticeable owner-reported flicker;
it ends much sooner, while the267-second recording keeps exercising the problem.
The synthetic maximum displaced-pixel count can actually be larger in this
emulator. We cannot infer human visual salience or Windows settings from that
count. The owner's photograph itself is not attached here; its described symptom
is reproduced as a class, not matched pixel-for-pixel. Exact perceived severity
and Windows acceptance require the owner to test **M011 TIMING / LOCAL / AUDIO**.

## Audio cause: digital stream versus emulated output

No production PCM/mixer/clock source was changed. Exact independent integer mixing
checks the source streams, event positions, gain ramps, truncation toward zero,
written FIFO words and consumed samples. Both M010 and final M011 checked
4,419,952consumed samples /1,104,984words, with **zero mismatches**. A constant
15sample startup advance (0.915527ms) is recorded explicitly, not fitted per
window; it stays within the existing silent pre-roll and one FIFO capacity.
The test rejects audible prefix loss, skipped/repeated samples/word positions,
wrong gains, source corruption and clock discontinuities. Complete request-clock
drift is0cycles, periods1022–1026cycles including host event-processing variation.
This records existing startup behavior rather than adding a new audio offset.

Host observation of mGBA0.10.1 shows its FIFO callback receiving a lateness argument,
then calculating PWM slot placement with `mTimingUntil(sampleEvent)-1` without
compensating that lateness. In the M010 failing excerpt, remaining time ranges
-14..4cycles and callback lateness reaches18cycles; crossing this boundary makes
PWM slots repeat/drop values even though the FIFO source sequence is correct.
In final M011at the same late passage, remaining time is597..643cycles, lateness
up to46cycles: different execution/start phase moves the primary case away from
that edge. It is not an engine-level guarantee that every future binary layout
will avoid the emulator artifact.

Controlled diagnostic: compensate only the emulator callback's slot timestamp
by its supplied lateness, restore the event deadline afterward, and keep the
same ROM, source audio, inputs, event trace and capture clock. M010's original
232.665039s correlation rises0.909975→0.991170; minimum correlation over that full
model is0.986496. Event CSV and timing CSV are byte-identical. No time is added
to the emulated GBA. The output waveform actually changes; this is not an analyzer
filter or a threshold relaxation. It causally identifies an emulated output timing
artifact rather than incorrect mixer arithmetic. No human audition was performed.

Final M011ordinary unmodified mGBA: all eight primary real waveform scenarios
and four public synthetic models pass unchanged >0.94correlation /<1ms residual
limits. Beginning/middle/end synchronization, clipping and ordinary-underrun checks
pass; fixed-mix compatibility passes its original limits. Additional ordinary
common-backing comparisons still fail:

- `scoring`,135.874939s:0.9976103against>0.999; scale0.994378.
- `wrong`,128.039001s:0.9988558against>0.999; scale1.001071.
- `reactive`: strict additional comparison passes.

Applying the same emulator-only correction to the separate M011miss/scoring/wrong
captures makes both additional comparisons pass, with minimum correlations
0.9999964and0.9999754respectively. Their event and timing CSVs remain byte-identical
to ordinary runs. This explains the residual comparison failures, but ordinary
unmodified-emulator results remain failures in the report. The inspected0.10.5
source retains the same uncompensated expression; that version/Windows GUI was
not tested. Do not promise that an emulator upgrade fixes it.

Reference: [mGBA0.10.1 audio implementation](https://github.com/mgba-emu/mgba/blob/0.10.1/src/gba/audio.c),
`GBAAudioSampleFIFO`. Installed headers/library are Debian0.10.1+dfsg-1+deb12u1.
The optional diagnostic correction in hardware_tap.c is never enabled for normal
acceptance captures, never part of the ROM, and not presented as a shipped audio
repair. No NOP/phase-delay workaround, altered music, relaxed test window or
replacement recording was inserted. **QA-010-004 remains open as an emulator
compatibility/release-validation gate; Outcome B is deliberate.**

### Negative evidence

Ten new public host tests include a correct reference and reject a consumed/written byte flip, repeated sample,
clock jump, unmuted full mix, missing backing, wrong fixed startup offset, source
corruption and absent observations. Substituting an actual full-guitar capture
for the muted mixed capture fails the unchanged waveform analyzer. Existing HUD,
results, tail and diagnostic hidden-layer injections all fail as expected.
Shifting the affine DMA source by one row leaves DMA active but produces569/569
bad frames (worst395pixels); disabling it triggers the actual-highway presence
check. These intentional failures are separate from ordinary strict audio failures.

## Complete regression and performance

108Python tests and8C++ ASan/UBSan programs pass. Ten normal real full-song
scenarios,17public synthetic/error scenarios, five input-diagnostic scenarios and
three36000frame Original Demo runs pass. Added assertions require DMA0/3 to be
released at results, diagnostic mode and Original. Fixed-mix /silent395Perfect and
395Miss compatibility, replay/menu, interrupted-session/error screens and fresh
replay audio pass. Original resolves699Perfect /699Miss /mixed exactly once and
continues playing its existing music. No Windows human play or physical GBA test.

All-Perfect holds:395Perfect,78completed holds,585bonus,15815total,395combo,
Full Combo/All Perfect. Early-release run:395Perfect,78early,212bonus,15442total,
combo/guitar preserved. M010's scripted early run had216bonus; the faster/different
poll phase observes one quarter-second boundary earlier. The independent interval
oracle reconstructs212from actual hit/release snapshots; scoring/250ms/grace
constants did not change. Full taps15230, allGood7615, allMiss0. Public fixture
remains512(470head+42hold), five complete /one intentional overlap retirement.

| Measurement | M010 | M011 |
| --- | ---: | ---: |
| Synthetic ROM | 814980bytes | 821556bytes |
| Private real ROM | 9178392bytes | 9184976bytes |
| Linked IWRAM real/synthetic | 27076/26660 | 27104/26688 |
| EWRAM payload real/synthetic | 3464/3096 | 9264/8896 (+padding) |
| Real maximum foreground, across normal scenarios | 170560cycles | 163456cycles (58.19%;9.74ms) |
| Real per-run means | 99995.5–104720.5 | 103054.7–107203.5cycles |
| Synthetic normal maximum foreground | 233728 | 219648cycles (78.20%;13.09ms) |
| Normal maximum reactive refill | 1472 | 1472cycles |
| Full-hold refill mean | 1342.36 paired baseline | 1383.68cycles |
| Ordinary underruns | 0 | 0 |
| Tail strips real/synthetic peak | 11/31 | 11/31, zero overflow |
| Rearm misses /latest entry /maximum cost | Not applicable | 0 /VCOUNT162 /2048cycles |

Means increase slightly because publishing a full table adds fixed work; peaks
improve by removing CPU scanline IRQ interference. Foreground profiling includes
overlapping IRQ/DMA stalls but excludes VSync waiting and the separate rearm call.
This is not complete CPU utilization, nor measured hardware frame time. No measured
foreground interval exceeds one280896cycle frame. Runtime stack high-water remains
unmeasured. Current finite charts pass; future denser charts require fresh budgets.

Public SHA256:
`a59989d631183bc02272866022ad5e03347b2a177f2b0cb6a7143c1950658f09`.
Private SHA256:
`c6112dbc98baa5643ea631fa5a02b9fd2a793e46d46b420e67c4e2f331ceac03`.
Native builds and clean pinned Docker source exports produce identical ROMs.
The actual owner ZIP was prepared/built with the exact two commands in the Windows
guide from a clean Linux export, reproducing the private hash. Different Windows/
Ubuntu FFmpeg versions may change conversion bytes; GUI installation was not tested.

## Delivery, owner verification and next priority

Public review: standard synthetic ROM, full source reference, native before/after
screenshots,60-frame sequences, logs, comparison and Windows instructions. Long
artificial diagnostic ROMs are not playable song releases. No new Cream recording,
chart package, event timeline, waveform capture or private ROM is published.
Private transfer is unsupported here; do not mistake a workspace path for a
verified download. Use the [Windows local build](RELEASE_PROCESS.md#windows-11--build-the-owners-cream-zip-locally).

Owner: confirm M011 TIMING, exercise the chord diagnostic, complete the public
song/results/replay/menu, then build the local Cream ROM and play all the way
through while watching the upper highway and listening for glitches. Record mGBA
version, any problem time and a short recording if it recurs. Manual acceptance
remains pending. The browser comparison and native synthetic sequences are visual
aids, not substitutes for this acceptance.

Stable integration is **not yet recommended**: ordinary emulator strict checks,
owner acceptance, physical hardware/stack measurements and historical asset rights
remain outstanding. No repository consolidation, main merge, stable tag, branch
rewrite or default-branch change was performed. Next engineering priority is
qualified emulator/capture compatibility validation and owner/hardware playtest;
then revisit approved feedback polish in a separately authorized mission.

Fresh verified Mission009 reactive baseline was also rerun with the unchanged analyzer and passes; this is a new observation, not an assumption based on historical logs.
