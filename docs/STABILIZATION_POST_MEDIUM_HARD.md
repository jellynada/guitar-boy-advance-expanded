# Post Medium/Hard stabilization candidate

Frozen starting source:3ed8be72f9652ada15c32ef4f77bbafddc2615bf.
Branch:stabilization-post-medium-hard. No merge or stable/hardware acceptance.

Measured baseline Cream initialization costs:46400cycles for state setup,
415488 for repeatedly deriving immutable chart end bounds,15296 for other state,
62848 for floor setup,347392 for font expansion and71680 for scanline/audio setup.
This spans multiple frames while gameMode already identifies gameplay. The old
short-chord tests can place both edges inside initialization; the label observer
can inspect a partial raster. Thus both runtime unresponsiveness during setup
and observing an intermediate scene contribute. Four delayed diagnostic frames
were evidence, not a fix. Source tests/audio_emulator.c and physical_emulator.c
remain unchanged for the original after-fix regressions.

The candidate computes immutable per-choice end bounds and all static font tiles
once at boot. Initialization still performs all resets, labels, palettes, controls
and fresh audio state. importedReady is0 during initialization/selector/results
and1 only after the first complete imported render table is committed in VBlank.
It remains1 during pause. A framebuffer observer must compose the raster after
that commit before inspecting pixels. The new readiness observer follows this
condition with a bounded failure timeout, not a fixed delay. Original observers
are also rerun unchanged. The contract does not imply that gameMode alone means
initialization is complete.

Baseline profiled Hard's worst frame at125.814209s spent approximately18624cycles
in judgment/completion,17088 in HUD/buttons,4608 in camera work,73024 in heads,
114240 in tails and59776 in affine/table preparation. Profiling is in an isolated
instrumented snapshot and is not shipped. Unmodified baseline peak:287040cycles,
above the280896-cycle frame deadline. Final acceptance uses unprofiled ROMs.

Only the highway camera Z changes during imported play. The exact affine formula
has dy=Z+constant; every other table field is unchanged for fixed camera X/Y,
u.x/u.z/v.y/w.y and horizon. The candidate caches that table and updates each
active row's dy by the exact Z delta. Any dependency/table/bounds change or risk
of signed overflow forces the original full calculation. Scene stop/start
invalidates the cache. Original Demo still calls its original calculation.
No row, head, tail, blend/DMA publication, judgment precision or audio operation
is skipped. Unit tests compare entire tables including unchanged fields and
exercise every invalidation key and overflow fallback.

See evidence/stabilization/cream-conflicts.md and JSON for exact source/runtime
times, source ticks, original note indices, combinations and sustain ends.
Medium has11opposing chords and Hard14; no additional opposing hold/onset
interaction occurs in this file. These charts' maximum head chords are2/3.
The source charts and approved controls are unchanged; native Medium/Hard still
cannot be completed physically on a conventional D-pad without a policy change.

Recommendation pending owner approval: preserve every native input and create a
separately named/versioned handheld-derived chart offline only. Prefer deterministic
minimum-cost reassignment of a conflicting lane to a genuinely free feasible
lane, preserving times/durations/counts and avoiding new same-lane overlaps.
Fail explicitly if no solution exists. This changes fret identity/shape and may
alter fingering patterns, even though musical timing is preserved. Retiming
conflicting heads into a roll changes rhythm and can still conflict with holds;
shortening holds loses intended sustain phrasing. Changing controls violates this
gate; dropping/merging notes or automatic chord success is rejected. A derived
chart requires a new explicit adaptation/provenance contract because the existing
native adapter intentionally rejects rewritten source lanes. No adaptation or
new import policy is implemented here; wait for owner approval.

The strict emulator audio issue remains a separate gate. Report exact mixer/FIFO
sample verification independently from analog/PWM/resampled output correlations.
No acceptance thresholds, PCM formats, source music, score rules, judgment windows
or diagnostic emulator fixes are changed. Final measurements and outcomes follow
in the verification record; no claim is made until those runs finish.

## Verification record: engine e4cc5771aaacf18301b2dae6110538e78b38a834

Final documentation/tool-only follow-up is identified in the build manifests.
Its ROMs must match this tested engine outside the40-byte revision marker and
are rechecked after packaging. Profile snapshots are separate, instrumented,
non-delivery builds; their stage reads have64-cycle resolution and additional
marker overhead. All main acceptance runs below use unmodified mGBA0.10.1 and
unprofiled ROMs. No timing padding or assertion/window/threshold relaxation.

### Original restart failures versus corrected observers

The original frozen37-case matrix had27passes and10Cream process failures at
`audio_emulator.c:262`; the original Cream glyph observer also failed. The same
unchanged executables/scripts now pass all37cases and both profiles' physical/
label checks. This is separate from the new20-epoch importedReady observer,
which also passes and is added to extracted-public-ROM CI smoke. Source hashes
for these old observers and gameplay interfaces are recorded in
`unchanged-interfaces.json`. The baseline four-extra-frame diagnostics remain
cause analysis, never a shipped test correction. GameMode is a scene identity,
not the readiness condition. No test was changed to delay away the ten failures.

### Deadline evidence

| Actual native chart | Baseline perfect peak | Candidate perfect peak |
| --- | ---: | ---: |
| Easy395 |173312|137088|
| Medium686 |261568|225152|
| Hard878 |287040|249280|

Additional native Hard stress: all-miss+pause282432→243840cycles;
mixed hits/misses/wrong inputs+pause286016→256448cycles. The highest observed
candidate foreground cost is256448, below280896 by24448cycles (~8.70%). This
fits the intended deadline in the measured full-song/host-input workloads;
it is not a proof for every possible key trace, chart, hardware or future code.
No hidden frame skip, tail/head reduction or precision change was introduced.

| Instrumented Hard distribution | Before | After |
| --- | ---: | ---: |
| Mean |150787|114208|
| Median |143296|106752|
| P90 |197824|161536|
| P95 |221805|185344|
| P99 |257321|221497|
| P99.9 |274873|239026|
| Maximum |287552|249856|
| Polls over280896 |7|0|

The exact JSON is authoritative; percentiles are from completed full-song polls,
not a moving average substituted for deadline checks. The worst baseline
profiled section is near125.814s. The top10heavy frames, visible heads, strips
and all subsystem maxima/means are retained in performance-profile.json.
Affine/table preparation averages fall from58300 to21601cycles. Head/tail work
remains enabled; those systems are not the optimization. Source-row reuse is
algebraically exact. Timer3 wall-cycle measurements include interrupt and DMA
stall time occurring inside foreground intervals, not exclusive instruction
counts. Refill IRQ maxima remain1408cycles. VBlank DMA re-arm maximum2048cycles,
latest line162, misses0 in the full native graphics tests; no new DMA/IRQ/timer.

All full Cream Easy/Medium/Hard highway scans have0displaced pixels; Medium/Hard
observe20/27peak sustain strips, no overflow and no audio underrun. Original
699-note Demo Perfect/miss/mixed36000-frame tests pass. Both three-difficulty
packages (real Cream and original synthetic) pass all12menu-aware smoke cases,
including alias handoff, short/eight pauses, paused exit and completion. The
standalone menu driver passes Hard replay and switching back to Easy. Complete
regular host suite:165Python tests and12ASan/UBSan programs pass. A separate
private-data trace-replay sanitizer executable passes three external captures.

### Easy scoring reference and trace phase

Scoring, judgment, sustain and controls headers are byte-identical to the frozen
source. Replaying the frozen native Easy musical-time/input trace through the
candidate core gives exactly15815points,585hold bonus and78completed holds.
The frozen legacy observer's captured trace reconstructs15811/581; the faster
candidate's new legacy capture reconstructs15831/601. Both have395Perfect and
78completed holds. Every recorded timestamp/statistic in the legacy traces is
checked by the sanitizer replay. These differing totals follow the inherited
rule that hold accumulation starts at the actual hit tick: a Perfect window
contains different possible fractional hold lengths. Startup/render work changes
poll/sample phase; no score rule or chart timing was rewritten to force one
number. Do not call every all-Perfect input trace a universal15815-point result.
The exact frozen reference remains reproducible; this limitation remains visible.

### Audio investigation: digital versus output

The ordinary output matrix is **10/15PASS,5FAIL**, versus14/15 on the frozen
source. All4public and6/8Cream primary waveform comparisons pass. Candidate
scoring primary fails at68.412048s (correlation0.877921); reactive primary at
164.682556s (0.870847), required>0.94. All3stricter backing comparisons fail
(two at those same primary windows); wrong-input common-backing correlation is
0.994403 at65.281189s, required>0.999. Time-error limits are unchanged. This
candidate does not have an all-green ordinary emulator audio matrix.

Independent exact checks of each unmodified candidate scoring/wrong/reactive
trace verify4419952consumed samples and1104984mixed words:0digital/mixer
mismatches; request periods1022–1026cycles, full-song drift0. Explicit inherited
silent startup advance15samples is not fitted per window. Current and frozen
chart/header/guitar/backing hashes match. Generic native All shares those exact
PCM streams. No transport, format, volume, gating ramp or recording was changed.

The frozen failed wrong-input trace likewise passes exact FIFO verification.
A host-only diagnostic corrects mGBA0.10.1's uncompensated FIFO event lateness;
on the exact frozen ROM it makes the strict comparison pass. On the exact
candidate ROM it makes all3failed mixed-scenario output comparisons pass,
including the same thresholds and common-backing reference. Diagnostic captures
of the frozen ROM still exit134 at the original post-song restart assertion:
that is not counted as a successful gameplay regression. Their completed audio
capture and exact/output analyses are separate results. No emulator correction
is included in shipped ROMs or used for normal acceptance. Layout/event-phase
sensitivity explains why the failing output window changes after optimization;
this is evidence for an emulator output-stage issue, not permission to describe
it as resolved. Alternate unmodified emulator versions and physical listening
remain required. Do not phase-pad game code to make this model pass.

### Delivery, hardware and integration gates

The source branch alone is pushed. The existing synthetic Actions workflow now
also runs on this stabilization branch; its extracted-ROM checks include the
new readiness observer. It uploads only the public synthetic review package,
never owner recordings/prepared songs/private ROMs. Local public packages are
inventory/hash/CRC/extraction checked and emulated. An actual GitHub artifact
must be separately confirmed downloadable; a local path is not that proof.

Real Cream Easy and native All profiles are built with owner-supplied audio.
The preferred all-difficulty player candidate is the Song-Private ROM: choose
Easy for a fully playable handheld chart. Native Medium/Hard still contain the
reported opposing chords. A fresh-password AES256 ZIP is prepared and tested
locally with independent7-Zip extraction and exact ROM hashes. Encryption does
not authorize public recording distribution. No private upload/attachment route
is configured in this session, so private download is blocked; no old/synthetic
ROM is substituted. The Windows one-click launcher is unchanged as fallback;
actual Windows GUI execution is not claimed.

Remaining owner gates: approve a conflict-adaptation policy before any derived
chart work; obtain the exact candidate through an authorized private route;
test actual GBA/flash-cartridge Easy controls, muting/recovery, holds, pause/
resume (held/new/released frets and long/near-end pause), results/replay/rapid
exits, graphics and Original Demo; use the original playable synthetic charts
for Medium/Hard alias/chord ergonomics and spacing. Native opposing-direction
charts cannot receive full handheld-playability acceptance as-is. Observe real
sound and timing; no emulator result accepts hardware. Review the documented
ordinary audio failures explicitly before integration. Main/develop and frozen
medium-hard-controls stay unchanged. Only after owner acceptance and explicit
approval should one reviewed source PR integrate this stabilization chain into
develop; never merge artifact branches, force-push, auto-release or start a
feature mission from this task.

Silent fallback was separately rebuilt and exercised through eight pause/resume
cycles: 240 frozen-state checks, 25 Perfect heads and final score 512; audio
remains stopped as intended. No fallback assets are substituted in Cream builds.
