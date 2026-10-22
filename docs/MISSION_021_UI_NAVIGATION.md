# Mission 021: UI/navigation development candidate

Based on accepted develop `d167d269f23b3d0f32d2753e6233f7f21771cd3d`. Owner review only: no automatic merge or release. RC2 remains immutable, SHA-256 `9c4af95ff97eddd266dca3d7491ac9a5b1256f417684aae51b7c126443afafde`.

## Implemented navigation

Boot -> Title -> START -> Main (Play, Options, Credits). Play -> Song Select -> Difficulty -> existing count-in/gameplay. B backs from Difficulty to the same song, Songs to Main, Main to Title, and Options/Credits to Main. Pause: Resume, Restart Song, Quit to Song Select. Results: Retry, Change Difficulty, Song Select, Main Menu. Results B shortcuts to Songs. No automatic replay or menu music.

UP/DOWN moves once per fresh press, wraps and does not repeat while held. A/START confirms. Confirm+Back and menu START+SELECT are ignored. Opposite directions do not move; direction+confirm moves only. Transitions seed all held keys until released. Gameplay retains START+SELECT exit, START pause/resume and paused SELECT exit. Paused B cancels a destructive highlight and stays paused; START always resumes. Fresh A/B during Pause now operate its menu. Lane mappings remain Easy LEFT/B/A; Medium LEFT/RIGHT/B/A; Hard LEFT/UP-or-DOWN/RIGHT/B/A.

Options contains real control/build information, A opens the existing input diagnostic. Private profiles retain SELECT for the legacy Original diagnostic; START+SELECT exits diagnostics. Credits identify startfliing's original project and jellynada's expanded source without inventing music rights. No final artwork or new settings.

## Catalog and naming

Static `UiNav::Catalog` has ID, title, optional artist, duration, difficulty mask, availability and asset reference. Maximum 32 entries/five visible rows; null/empty required names, unavailable assets, invalid masks and invalid selection cannot launch. Text is clipped to available columns, no dynamic allocation. Host tests cover eight metadata entries, filtering, scrolling, bounds, selection context and long strings. Runtime reference 1 binds only the verified imported package. Multi-song audio/chart loading is deferred.

Copper Circuit keeps internal identifiers and displays **Synth Demo** in new public builds. The separate existing Easy synthetic regression fixture maps to **Synth Demo 2** only in that profile; it remains retained and is not added to the current public/Cream ROM. The legacy Original recording is not renamed synthetic. Each delivered ROM lists exactly one genuinely playable song. Public metadata is fixed and rejects private-package input; private metadata comes from the verified normalized package.

Public: original Copper Circuit, 75 seconds plus existing count-in, Easy/Medium/Hard heads 86/171/335. Private: full Sunshine of Your Love, 267.271911621 seconds plus existing count-in, heads 395/686/878 and holds 78/172/175. Prepared stems/charts/adaptations are unchanged. No PCM, mixer, gain, sample-rate, codec, scoring, judgments or chart-timing source changes.

## Resource ownership and measured limits

Menus/results use existing BG1 character block 0/map31, font tiles128..224 and palette15 (BG241 white,242 black), BG0/BG2/OBJ disabled. No highway DMA, active PCM timers or refill IRQ in menus. Existing VBlank remains. Gameplay keeps BG0 character block1/map30 HUD/receptors, BG1 character block0/map31 mask, affine BG2 character block2/map24. DMA0 affine/DMA3 blend; timers0 PCM/1 grouping/2 extension/3 profiling unchanged. OAM heads0..31/tails32..127 and OBJ allocations unchanged. No new DMA/timer/IRQ/OAM ownership.

Pause saves/restores 26x9 BG0 cells in EWRAM; opaque font uses character block1 tiles225..320, separate from receptor tiles below128 and transparent font129..224. Affine/OBJ assets are untouched. Accepted freeze/resume order, scanline restoration and physical/sustain input seeding are retained. Restart/quit stop the old scene and reuse fresh initialization. Results masks/acknowledges Timer1 after audio ends: Tonc can restore its pre-EOF enable bit on ISR return. PCM transport code remains unchanged.

Preliminary native measurements; final versioned identities and reruns are recorded in the owner-local report and CI manifests:

| Resource | Public | Full private |
|---|---:|---:|
| Static IWRAM (.iwram+.bss+.data) | 8276 bytes | 27812 bytes |
| Additional static IWRAM vs same native baseline | 0 | 0 |
| Static EWRAM | 7324 bytes | 10396 bytes |
| Additional EWRAM | 308 bytes | 308 bytes |
| ROM size before final identity string | 2648548 bytes | 9218536 bytes |
| Private ROM growth | - | 4676 bytes |
| Minimum observed untouched user stack | 23472 bytes | 3884 bytes |
| Monitored IRQ touched/untouched | 40/120 bytes | 40/120 bytes |

Same-environment full-private baseline has 3700 untouched user-stack bytes: observed margin improves. M020 toolchain/profile numbers differ and neither is a whole-stack proof. The resource contract governs BOTH public and private builds. Changes are below zero-extra-IWRAM,4KiB-EWRAM,256KiB-ROM proposals. No menu rendering runs within measured playback work. Mixed private Easy/Medium/Hard peaks:136256/233536/252480 cycles versus same-environment baseline135104/233728/253632; all below280896/frame and the8192-cycle change-control increment. Full receipts include perfect-input peaks too. Six graphics observations/profile require zero displaced pixels, underruns and scanline deadline misses. Private refill observed peak1536 cycles; audio IRQ source unchanged. Emulator maxima are not physical worst-case limits.

## Tests and reproducible evidence

All prior host engine checks remain in `tests/check.sh`, followed by UI reducer/metadata checks. Native Windows passes thirteen existing C++ programs plus UI navigation without sanitizers. Linux CI runs the original ASan/UBSan flags and complete Python suite. Windows Python limitations (symlink privileges, POSIX fake executable, LF fixture hash under CRLF) remain documented; no tests/thresholds are weakened to hide them.

Actual-candidate matrix/profile:30 pause/stress cases,6 full graphics runs,3 eight-pause stack runs,20 readiness epochs, navigation with20 start/quit loops and12 full completions (all3 difficulties x all4 Results actions), held inputs and private physical/legacy checks. Exact digital oracle:15 cases/profile, original `analyze_fifo.py`, startup advance15, independently observed FIFO words and consumed PCM, no lateness correction. Windows host-only static wrappers use unchanged stock mGBA0.10.5; CI uses stock Debian0.10.1. Observers never enter a ROM.

`tests/build_ui_probes.py` retains original observers and generates explicit navigation adapters. Menu travel and Results text coordinates change. Single-difficulty observer binds to the selected active Easy pointers in an all-difficulty package. Legacy entry waits for its real initialization handoff. Pause freeze probes carry entry keys instead of generating fresh A/B menu actions; frozen timer/counter/framebuffer assertions and real post-resume edge assertions remain. Score/combo/sustain/guitar/FIFO/clock assertions are retained. Original fixtures/test songs are not deleted. The forged early-EOF inconsistency observer remains on its original non-cut 25-head synthetic fixture: a finite-cut build deliberately resolves pending heads at declared EOF and can exceed the observer's 16-event trace ring under that artificial injection. It is not an equivalent stimulus on a finite-cut song. All seventeen inherited modes run on the preserved fixture. Any unresolved candidate diagnostic is reported in local receipts, not called a pass.

**Historical strict ordinary output is9/15, release-blocking.** Candidate navigation shifts the initial emulated phase, so retain its actual15-case result matrix. Preliminary native public result10/15 does not clear release. Private output failures are retained too. Original correlation>.94,sub-ms alignment/gain/mute/recovery assertions remain. Digital correctness does not prove speaker-output transparency or real-GBA acceptance. No failed output gate is silently made green.

`.github/workflows/m021-ui.yml` compiles the actual checked-out commit and exercises that ROM; manifest verifies exact embedded identity, header, stems, hashes and public isolation. Strict output is a separate failing job if any case fails. M020 runtime-equality integration applies to its original PR or explicit dispatch, since new UI cannot equal old RC2 bytes. Historical synthetic CI defers this branch to the actual-candidate workflow. Frozen RC2 workflow/artifacts remain independent. CI uses original Copper Circuit exclusively; private audio/charts/ROM/captures stay local.

Every candidate manifest records source commit,ROM/ELF/symbol hashes,prepared-manifest hash,profile and toolchain. Missing/changed artifacts,stale source markers,invalid cartridge headers or absent stems fail verification. Public rejects private markers and legacy symbols. Exact final tested SHA,Windows paths,ROM hashes,toolchain logs and rerun results are in owner-local `Build-Reports/Mission-021` (outside Git); CI manifests contain their own exact candidate identity. This avoids self-referential source commits and public personal paths/private hashes.

## Review/rollback and deferred work

Main/develop remain untouched. Before an approved merge, use preserved accepted ROMs as rollback. Accepted baseline is d167d269f23b3d0f32d2753e6233f7f21771cd3d; if a future approved merge requires rollback,use a normal merge revert with parent1,no force push or history rewrite. See the separate owner checklist. Real-GBA acceptance,wider stack/bus/timing/audio validation,multi-song loading and final artwork remain future work. No release is approved by this branch.
