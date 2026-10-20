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
