# M021 closeout review and controlled integration handoff

**READY FOR DEVELOPMENT MERGE - WITH DOCUMENTED AUDIO LIMITATION**, subject to the final review-only head's CI and owner approval. Technical verdict: **KNOWN BOUNDED LIMITATION - NO NEW ENGINE REGRESSION DEMONSTRATED**. Strict output certification remains failed; the overall workflow is not all green.

Reviewed runtime ea1832bf8454c82a84f0a5ae5142917853e44a60 descends directly from accepted develop d167d269f23b3d0f32d2753e6233f7f21771cd3d. Remote main/develop and PR4 were unchanged at audit entry. PR source changes are scoped to UI/catalog/scene lifecycle, display metadata/build identity and exact-candidate verification. No compression, multi-song loader, scoring/clock/control/judgment/mixer/stem preparation redesign is present. Private contents and owner-specific hashes/paths remain outside public history.

## Source and lifecycle review

The pure bounded navigation reducer is separate from scene drawing and imported-chart transport. Catalog bounds, available-mask filtering, one-song behavior, held START/A, opposing/conflicting controls and long names are covered by host tests. Only packaged assets appear. Public Synth Demo/retained separate Synth Demo2 naming does not fabricate a second runtime song.

`source/main.cpp` reuses accepted fresh-session initialization and held-input resume order. Restart/quit stop old PCM/scanline/scene ownership; Results retains final statistics until an action. The one transport-adjacent change masks/acknowledges a refill IRQ after EOF because the dispatcher can restore its previous enable bit. No new audio ISR work is added. Results navigation and pause overlay are bounded. The exact public/private ROM tests exercise all three difficulties, pause choices, four Results actions, multiple complete loops and resource cleanup. No verified menu defect requires rewriting working behavior.

Build metadata is display-only. Public builds reject private metadata and validate actual embedded original stems, ROM/header/source identity and artifact hashes. CI checks out and compiles the candidate head, not only RC2. The frozen M020 equality gate is explicitly separate and scoped to its original foundation PR/dispatch; the M021 release-output job remains nonzero when any case fails. The audit restores the original public final reference window76.7s (was75.2s), with a regression test; all45 original-window replays retain9/11/10 pass totals. No threshold or comparator is relaxed.

## Resources, same-environment comparisons

| Comparison | Baseline | M021 | Change |
|---|---:|---:|---:|
| Pinned Linux public static IWRAM section sum | 8284 | 8284 | 0 |
| Pinned Linux public EWRAM | 7016 | 7324 | +308 |
| Native full-private static IWRAM section sum | 27812 | 27812 | 0 |
| Native full-private EWRAM | 10088 | 10396 | +308 |

Section sums exclude linker alignment gaps; historical contract totals may include them. Like-for-like growth is zero IWRAM and308 bytes EWRAM, below4KiB. Native private ROM growth is4740 bytes, below256KiB. No new DMA, timer, OAM or audio IRQ allocation. Existing BG/font/palette/tile contracts remain as in the implementation report: pause uses BG0 character-block1 opaque tiles225..320 with receptor tiles below128 and transparent tiles129..224; menus/results use existing BG1/map31. Affine highway/OBJ ownership is unchanged.

Retained native foreground peaks Easy/Medium/Hard: public120064/149312/158464; private137664/233536/254016, all below280896 cycles/frame. Same-environment private mixed baseline135104/233728/253632 versus M021136256/233536/252480; largest increase1152, below8192 change-control proposal. No observed underruns, scanline deadline misses or displaced pixels. Native minimum observed untouched user stack: public23472, private3884 versus same-environment private baseline3700; IRQ40/160 monitored bytes touched. Pinned CI public minimum23448. These are reviewed-path emulator observations, not worst-case hardware or whole-stack proofs. The contract applies to both original public content and full private builds.

## Fresh versus retained evidence

Fresh closeout: fetched ancestry/PR/remote states; source/sensitive-blob review; all1062 Playlist hashes and modification times, original ZIP/old private/RC2 hashes;1875 files in the three original M021 public artifacts scanned; seven archives digest-verified;45 original-window public comparator replays;34 focused full digital/FIFO checks, including same-ROM cross-host and title-delay controls; two corrected read-only PWM captures with exact byte-equivalent FIFO/raw/event/transport output; ELF section comparison; seven focused metadata/policy unit tests. Full per-file identities and scripts are owner-local.

Retained exact-runtime evidence from the completed M021 run:83/83 native navigation/gameplay/graphics/stack/readiness/physical checks across public and full private; twelve complete songs/profile (all difficulties x all Results actions),20 start/quit loops/profile;30/30 native digital cases; four pause-edge checks;17 inherited engine emulator scenarios;14 native C++ programs. [Original CI](https://github.com/jellynada/guitar-boy-advance-expanded/actions/runs/39721249192) passes ASan/UBSan,224 Python tests (1 skip), retained fixture scenarios, candidate gameplay/resources and15 digital cases, with a deliberately failed strict output job11/15. Native Windows Python's POSIX/symlink/LF limitations are not substituted for the passing full Linux suite.

The final review-only head must rerun affected public checks in CI; its exact SHA/run and proposed merge-tree equality are recorded in the PR handoff/local final receipt. Game/build inputs remain byte-identical to ea1832b. Existing owner-played ROMs are preserved; no new private ROM is required merely for documentation/test-policy closeout.

## Audio decision and owner evidence

See [audio differential](M021_AUDIO_DIFFERENTIAL.md) for all15 scenarios/cases, every failure, changed case IDs and controlled phase experiments. Historical9/15, CI11/15 and native10/15 are not quality grades. The newly failing private Medium mixed comparison was investigated at the verified FIFO, pre-filter PWM and independent blip layers and matches the known stock slot-placement mechanism. No new incorrect digital samples, mixer corruption or accumulating clock drift was found. Independent replay retains4..5 signed16-unit error and is not an exact acceptance oracle. Formal release remains blocked.

See [owner feedback](M021_OWNER_ACCEPTANCE.md): positive RG SP/mGBA handheld emulator experience, not original GBA certification or invented exhaustive coverage.

## History-preserving handoff

Keep PR4 unmerged and auto-merge disabled. Once final checks are reviewed, owner approval must explicitly authorize a **normal merge commit into develop**, identifying the final PR head and expected develop d167d269f23b3d0f32d2753e6233f7f21771cd3d. Immediately before merging, reverify both heads and all mandatory development evidence; stop on movement/unexpected failure. The known failed formal-release gate is explicitly distinguished from development acceptance. Main is untouched and no release is authorized.

The proposed merge tree should equal the final head tree because develop is its ancestor; final handoff verifies this rather than calling an unexecuted merge commit tested. Runtime tests use exact committed head/artifacts; tree equality identifies equivalent source. The actual eventual merge SHA depends on owner approval and merge metadata. Rollback now is continuing to use preserved baseline ROMs. After a later approved merge, use a normal revert with parent1; never force-push/reset history. No graphics work, Mission022 or other feature work follows automatically.
