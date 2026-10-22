# Mission 022 closeout review

**Verdict: READY FOR OWNER DEVELOPMENT EXCEPTION REVIEW.**
**Recommendation A: RECOMMEND DEVELOPMENT EXCEPTION, subject to explicit owner acceptance.**
PR #5 remains draft and unmerged. This is not integration or release approval.

## Reviewed identity and scope

- Repository: jellynada/guitar-boy-advance-expanded.
- Reviewed executable source: `c4f900bbd99734353a8de38cf82d2629cd1eaf2d`.
- Accepted develop: `cf2ee6601753a2718f0e08f6c9f78ac791114e03`.
- Mission branch: `mission-022-multi-song`; [PR #5](https://github.com/jellynada/guitar-boy-advance-expanded/pull/5).
- This closeout adds documentation only. The commit containing these documents is a descendant of the executable snapshot above; the actual documentation head is recorded in the PR and owner-local closeout receipt. It is not the source identity embedded in the preserved playable ROMs.

The complete 26-file implementation diff and all eight implementation commits were reviewed. Intended changes bind catalog entries to per-song chart/PCM descriptors, select a 20-byte stopped-audio source, preserve existing single-song builds, and add collection generation/verification and actual-ROM observers. The private collection omits unused legacy audio storage. No unintended scoring, judgment, physical mapping, sample-clock, preparation-recipe or graphics-algorithm change was found. Source-selection indirection is an intended audio access change and has a measured cost; it is not described as free.

## Performance review

| Comparison | M021 cycles | M022 cycles | Difference |
| --- | ---: | ---: | ---: |
| Original broader Hard profile peak | 254,016 | 266,432 | +12,416 |
| Original Hard case 28 | 252,544 | 266,432 | +13,888 |
| Controlled busy-frame diagnostic | 266,112 | 266,432 | +320 |
| Complete 60-phase Hard envelope | 271,360 | 270,848 | -512 |

The historical +8,192 allowance remains **failed**, by 4,224 cycles against the broader profile or 5,696 against the original same case. Diagnostic comparisons do not replace that gate.

The stress driver schedules additional physical-safe pulses by observer frame, while chart autoplay follows the PCM clock. Different initialization/readiness and audio/video phase move a wrong-input event and its HUD redraw onto a dense rendering frame in M022. The original named cases therefore do not have identical per-frame workloads.

Instruction-boundary attribution of the original difference is HUD +10,421, gameplay/event work +1,333, IRQ service +2,554, offset by 410 fewer rendering/table cycles. The 13,898 traced-cycle difference agrees with the 13,888 Timer3-counter difference within measurement granularity. The counter uses 64-cycle ticks; read-instruction boundaries and actual MMIO sampling points are not identical.

A one-frame input diagnostic causes the existing baseline to perform comparable busy rendering/event work at 266,112. It does not establish identical whole-song inputs, scoring state or PCM phase. The envelope compares the full tested stimulus family, not identical individual frames. All 120 Hard phase runs and 12 Medium phase controls pass the existing runtime assertions. Medium's original case-28 increase is also disclosed: 225,216 to 236,608 (+11,392); its six-phase sampled envelope is 237,952 to 240,512 (+2,560), not an exhaustive Medium sweep.

No unexplained large collection-only operation remains. The real PCM access cost is approximately 48 cycles per equivalent append16 call, with about 1,000 extra IRQ cycles in the matched busy interval. Descriptor binding and selected-chart boundary scanning happen during stopped initialization, not a repeated per-frame catalog search. The proposal in [M022_PERFORMANCE_EXCEPTION_PROPOSAL.md](M022_PERFORMANCE_EXCEPTION_PROPOSAL.md) preserves these distinctions.

## Actual remaining margin

The expanded candidate maximum is **270,848 foreground cycles**. Subtracting it from the nominal 280,896-cycle frame gives 10,048; that subtraction omits other frame work.

At the measured envelope winner, the ending timer-read instruction is **7,821 emulated cycles before the next VBlank**, before subsequent bookkeeping. The original 266,432-cycle peak leaves 12,325 at that boundary. No observed deadline miss makes either number a physical safety bound.

Targeted peak observations account for the full IRQ dispatcher even though Tonc executes callbacks in System mode. The candidate winner has 17 audio callbacks, entry lateness 79–114 cycles and callback durations 1,458–1,604 versus a 16,384-cycle refill period. Timer/FIFO ownership is unchanged. No underrun, sustain overflow, scanline deadline miss or stack collision is observed. Targeted main/IRQ stack watermarks and all detailed frame data remain owner-local. These are measured executions, not all-path proofs.

Native comparisons use the same devkitARM release 65/GCC 14.2.0 and stock mGBA 0.10.5 with the stock HLE BIOS. The retained M021 binaries identify ea1832bf8454c82a84f0a5ae5142917853e44a60; their runtime source/include/Makefile match accepted develop. Public CI separately uses the pinned toolchain image (application GCC 16.1.0) and stock Debian mGBA 0.10.1. Results from different toolchains are not pooled into the native CPU comparison.

## Functional and audio evidence

Public cartridge: Synth Demo is the original Copper Circuit composition with Easy/Medium/Hard. Synth Demo 2 is a distinct original synthetic fixture with Easy only. The manifest, actual active pointers, supported difficulty masks and complete runs establish real chart/audio binding; unsupported difficulties are not offered.

Owner-local cartridge: Synth Demo and the existing full-length private recording retain independent aligned guitar/backing PCM and Easy/Medium/Hard for the private track. Both can be launched and completed and switched without reboot in the automated paths. No recording was shortened, recompressed or prepared again.

Retained exact-executable verification, revalidated by receipt and binary hashes during closeout:

| Coverage | Public | Owner-local |
| --- | ---: | ---: |
| Matrix jobs plus physical pause-edge checks | 77 passed | 113 passed |
| Included exact digital PCM/FIFO cases | 20/20 | 30/30 |
| Full completion / Results-action scenarios | 16 | 24 |
| Launch/quit loops per ROM | 40 | 40 |
| Perfect/mixed graphics scenarios | 8, zero defects | 12, zero defects |

The 40-loop sequence covers both directions and has 20 adjacent cross-song changes; the observer's inherited “40 alternating switches” stdout label overstates distinct switches. Readiness waits are host-only observation changes, not gameplay shortcuts. Restart, Retry, Pause/Resume, Quit, completion, physical inputs, held confirmations, invalid indices, sustains/chords and score/clock resets are asserted.

All 50 native digital cases have zero mixer/sample mismatches and complete/segment clock drift, using unchanged startup advance 15 and no lateness correction. Ordinary per-frame observation produces byte-identical original/trace audio and event captures. Exact digital transport does not establish PWM, ordinary-output or analog equivalence.

[Retained exact-executable CI, attempt 2](https://github.com/jellynada/guitar-boy-advance-expanded/actions/runs/39736138575/attempts/2) passes 240 Python tests (1 declared skip), 14 ASan/UBSan programs, the public build and candidate gameplay/resources/digital checks. Its strict ordinary-output release gate remains **FAILED, 14/20** (first song 9/15, fixture 5/5). Native public remains **15/20**, native private **22/30**. Previously documented case-level differences from M021 remain unresolved. No comparator, reference window, threshold or failing case was changed.

This closeout freshly checks branch/source state, retained report integrity, actual ROM identities, all introduced commit blobs and public artifacts, and file preservation. It does not relabel retained emulation runs as fresh. There is no reason to repeat hours of native phase/runtime tests for documentation-only changes; the PR records any normal CI runs triggered on the documentation head separately.

## Security and preservation

Fresh closeout checks verify all 1,062 song-library files, 14 historical playable/prepared files, 22 historical Downloads ROMs, frozen RC2 and both delivered M022 ROM hashes. Recorded modification times match where available. The exact current playable paths and private media identities remain only in the owner-local report.

All 45 introduced/modified implementation-commit blobs were inspected for private PCM/chart signatures and personal paths. Retained public CI ZIP digests and 213 extracted file hashes match their audited inventory. No private recording, chart array, local capture, private ROM or personal Windows path was found in the reviewed public additions/artifacts. Detailed private measurements and reports stay outside tracked source. Historical reports are retained rather than overwritten.

## Resource constraints for future work

ROM capacity is not CPU capacity. Native public size remains 3,168,904 bytes, with 30,385,528 below 32 MiB. Measured unique public song costs remain 2,570,344 and 519,651 bytes. The [capacity study](MISSION_022_CAPACITY_STUDY.md) projects seven 2-minute, five 3-minute, four 4-minute or three 5-minute songs with a provisional additional 1 MiB art/code reserve. These are storage projections, not tested libraries, final song counts, or CPU/graphics allocations. Compression policy is unchanged.

The [M020 resource contract](M020_GRAPHICS_RESOURCE_CONTRACT.md) still applies to both public and owner-local builds. Its historical numbers do not supersede the newer Hard measurements. This exception grants **zero additional gameplay-frame graphics CPU cost**, no extra IRQ work, and no resource allocation.

| Resource | Existing ownership to preserve |
| --- | --- |
| Menu/title VRAM | Mode 0 BG1, character block 0 / screen block 31, existing UI font; restore gameplay state on scene exit |
| Gameplay BG VRAM/maps | BG0 character block 1 / map 30; BG1 block 0 / map 31; affine BG2 block 2 / map 24 with 64x64 map; preserve full map spans and halfword VRAM writes |
| Font/receptor tiles | Receptors and BG font ranges already reserved; BG glyph copies 129..224 and pause glyphs 225..319; no inferred free tiles |
| OBJ tiles/OAM | Notes tiles 0..128; tails 192..383; font payload starts at 512 with glyph references from 513. Heads reserve OAM 0..31, tails 32..127; no guaranteed spare entries |
| Palette | Existing lane banks, lane-five treatment and bank-15 text are owned; no bank presumed free |
| DMA | DMA0 affine and DMA3 blend at HBlank; DMA1/2 unused by imported software FIFO, but not globally free across legacy modes |
| Timers/IRQ | Timer0 sample clock, Timer1 refill grouping, Timer2 count extension, Timer3 profiling; no reassignment, new nesting or priority changes |
| RAM/stacks | No new IWRAM, per-frame heap, recursion or large automatic arrays; preserve measured public/private stack margins and explicit EWRAM ownership |

A separately approved static menu/title-art investigation is technically reasonable before a gameplay highway redesign: its transfer/decompression can be measured while gameplay, scanline DMA and PCM are stopped. It still needs an explicit VRAM/palette map, bounded screen-load time, and verified transitions restoring fonts, maps, palettes, OAM, IRQ/DMA and timers. A screen-load cost must not migrate into ongoing gameplay or HBlank. No art, decompression or graphics budget is allocated here.

After owner decisions and separately authorized integration, the likely next content validation is two full-length private songs, followed by separately measured graphics feasibility. Neither milestone is started or approved by this closeout. Added content must be profiled independently; spare ROM bytes are insufficient.

## Acceptance path

See [M022_OWNER_ACCEPTANCE.md](M022_OWNER_ACCEPTANCE.md). Only the two expected owner-local Song Select entries are confirmed on RG SP/mGBA; other M022 handheld actions remain pending. Prior successful M021 handheld reports are not M022 coverage.

The owner must explicitly decide the documented exception and disposition of pending handheld tests, then separately authorize a normal history-preserving PR #5 merge against reverified exact head/base and mandatory development checks. Keep draft status until that decision. Do not enable auto-merge, merge, modify develop/main directly, publish a release or start another mission.

Until then the accepted develop baseline and preserved ROMs remain the use/rollback points. If a future merge is authorized and must be undone, create a rollback branch, use `git revert -m 1 <actual_merge_sha>`, verify it and submit a normal rollback PR. No reset, force push or history rewriting.
