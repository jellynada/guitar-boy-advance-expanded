# Physical controls and logical lanes — Mission013

The chart describes **logical lane numbers**, not hardware buttons. Imported Easy
keeps its original lanes0/1/2, positions/colors, note times and sustain durations.
Only the hardware bindings change:

| Logical lane | Imported Easy | Original Demo |
| --- | --- | --- |
|0|LEFT|LEFT|
|1|B|RIGHT|
|2|A|A|
|3|not enabled|B|

## Runtime contract

`include/gameControls.hpp` owns the production button masks and Easy labels.
`include/physicalInput.hpp` provides fixed-size constexpr mapping and logical edge
calculation. It has no heap allocation, hardware reads, clocks or judgment policy.
Each binding is a physical-button bitmask. Any pressed alias holds that one lane.
Map raw held buttons first; then compare with **previous logical held state**:
pressed=current & ~previous, released=previous & ~current. Do not map raw physical
key_hit/key_released when a lane has aliases.

The existing gameplay judgment system already computes edges from logical held
masks and remains unchanged. Scene reset seeds held state so a button held before
start is not a fresh note press. Sustain processing receives the same logical
held mask as note judgments. Diagnostics use the shared logical edge operation.
Menu/replay navigation still uses A/Start and B/Select; it is not a chart lane.

Receptor activation reads the same EASY_BUTTONS table as gameplay. Existing Tonc
font tiles label the receptors LEFT/B/A below the circles; no new art, lane
position or highway projection is introduced. Six affected BG0 map cells are
saved and restored exactly on exit, rather than masking/clearing an entire row.
Labels are drawn once on scene initialization, not added to the per-frame loop.
Diagnostic masks use the same Easy label table. Its prompts now say LEFT+B,
LEFT+A, B+A, release-B/keep-A, rapid B and LEFT B A sequence.

## Chart/audio preservation

Importer, adapter, prepared header and PCM generation are unchanged. Public and
real prepared asset summaries/hashes are byte-identical to Mission012, including
the395-head/78-sustain chart header. Logical note records never get renumbered.
Historical normalized/adapted JSON retains old human-readable button annotations
for compatibility; those fields are not used for runtime input. Treat the engine
binding table, manifest physical_controls and visible labels as authoritative.
A future schema cleanup can remove those historical annotations separately.

## Future mappings: design/test only

Medium proposal: LEFT / RIGHT / B / A. Hard proposal:
LEFT / (UP or DOWN) / RIGHT / B / A. Neither difficulty is selectable or has a
production mapping table in this mission. Test-only fixtures exercise the generic
mapper with these proposals.

For Hard, UP and DOWN are OR aliases of one lane. UP→both→DOWN and direct
UP→DOWN handoffs produce neither an extra logical press nor a release while one
alias remains held. Only releasing both ends that lane. A sampled gap with neither
held is a real release. Other physical D-pad conflict/chart-playability rules,
new difficulty adaptation and full sustain-switch UX require their own mission.
Tests do not imply every injected opposite-direction combination is mechanically
possible on a real D-pad.

## Test coverage

Host tests independently enumerate1024 raw GBA masks and8192 previous/current
Easy edge cases, chords, staggered/overlapping holds, rapid B taps, held-at-reset,
Original mapping and test-only Medium/Hard alias handoffs. Sanitizers are enabled.
The emulator drives actual GBA key bits (LEFT32, B2, A1), not gameplay input RAM.
It verifies visible labels,8 receptor combinations, release-B/keep-A feedback,
exact BG0 restoration, all13 diagnostic outcomes, overlapping holds and Original
LEFT/RIGHT/A/B receptors. The old LEFT/A/B script must fail on this ROM.

The owner has **not yet accepted Mission013** on handheld. Prior Mission011
hardware acceptance belongs to that earlier build only. See the new mission's
owner checklist before any acceptance claim.
