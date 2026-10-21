# M020 proposed graphics resource contract

This is a proposal for later owner-approved branches, not authorization to add
graphics. Numbers are retained M019 measurements unless a newer M020 receipt
explicitly replaces them. Emulator maxima are not physical worst-case bounds.

| Resource | Public Copper Circuit / private full Cream | Initial change constraint |
|---|---|---|
| ROM, 32 MiB ceiling | 2,643,632 / 9,191,156 bytes; remaining 30,910,800 / 24,363,276 | Keep shared art compatible with the private profile; proposed first increment at most 256 KiB, with a new size check |
| Static IWRAM, 32 KiB total | 8,308 / 27,276 bytes, before runtime stacks and BIOS reservations | **Zero additional IWRAM initially**; do not treat 5,492 private bytes as free space |
| Static EWRAM, 256 KiB total | 7,016 / 9,600 bytes; arithmetic remainder excludes runtime/library needs | Proposed first increment at most 4 KiB static EWRAM; no new per-frame heap allocation; verify ELF placement |
| Main stack | Public 916 touched / 23,288 untouched; private 980 touched / 4,256 untouched in instrumented eight-pause runs | No new large automatic arrays or recursion; require both profiles' sentinel checks, retain at least the existing observed private margin until reviewed |
| IRQ stack | 40 of 160 monitored bytes touched; 120 untouched | No extra IRQ work or interrupt nesting; existing measurement is not a whole-stack proof |
| Foreground frame work | Frame 280,896 cycles; public soak peak 155,776, private Easy 137,088; 125,120 public observed remainder | Proposed first increment at most 8,192 measured cycles per frame (2.92% of frame), with **no** deadline regression; this is a change-control limit, not guaranteed safe additional work |
| Full private difficulty workload | Fresh M019 full-length private testing was Easy, not exhaustive Medium/Hard | Do not use Easy's peak as a private Hard bound; profile the intended full chart before approving it |
| Audio IRQ / scanline | Refill observed peak 1,472 cycles; 39-cycle minimum emulated HBlank remainder, zero late writes in retained transports | Do not spend apparent foreground slack inside HBlank or audio IRQ; measure dispatch/return separately if changed |
| DMA | Imported DMA0 affine and DMA3 blend; DMA1/2 disabled for software FIFO; legacy Maxmod has separate ownership | No newly allocated DMA channel initially; disabled is not universally unowned across modes |
| Timers | Timer0 PCM, Timer1 refill grouping, Timer2 count extension, Timer3 profiling | No timer reassignment; no sample-rate or IRQ priority changes |
| OAM | 128 entries; heads reserve 0..31, tails 32..127; observed public heads 8/tails 12 and private tails 11 | **Zero guaranteed spare entries**; observed idle entries are reserved capacity, not available allocation |
| OBJ tiles | Existing notes 0..128, tails 192..383, font begins 513 | No overlap, renumbering, or inferred free ranges without an explicit allocation map and dense-hold checks |
| BG VRAM / maps | Gameplay BG0 character block1/map30, BG1 block0/map31, affine BG2 block2/map24 with 64x64 map | Preserve decompression destinations, map spans and halfword VRAM writes; inventory exact tile extents before allocating new art |
| Palettes | 256 BG and 256 OBJ colors; lane banks and bank15 text are in use | No palette bank presumed free; document indices and mode ownership before edits |
| Transitions | Scanline stop, PCM stop, readiness handoff, pause tile save/restore and fresh mode epoch already exist | Restore IRQ/DMA/timer/palette/OAM/BG ownership on exit, replay, pause and results; no stale source pointers |

The 8,192-cycle, 4-KiB and 256-KiB limits are conservative **proposals**, not
measurements or universal limits. If a change needs more, review its measured
impact first. The private stack and scanline margins, not the public ROM's large
apparent free RAM, govern initial risk.

For each visual increment: preserve immutable RC2 for comparison; change one
resource class; profile public all difficulties and the applicable private
profiles; run existing host/sanitizer, exact-ROM input/pause/results/graphics,
digital transport and unchanged output checks. Compare against the known output
failure set instead of treating a pre-existing failure as success. Reject new
failures, underruns, late scanline writes, tail overflow, displacement, reduced
stack margin or unexplained timing growth. Revert the visual commit normally and
repeat the prior measurement if a regression occurs. Large asset transfers belong
in a measured scene-load/VBlank schedule, not unbounded active-display work.

The M020 workflow intentionally rebuilds frozen RC2. Before any future visual
change can be accepted, CI must also build and execute **that candidate's exact
source**, with a separate identity and baseline comparison. A green frozen-RC2
job alone cannot validate new graphics code. Extend branch triggers and candidate
build coverage during the separately approved graphics-branch setup.

Physical bus contention, all-path stack high-water and worst-case hardware timing
remain unmeasured. Positive RC2 owner listening/playability improves confidence
but does not replace these measurements.
