# Mission 015: foundation audit and first slice

Audit date: 2026-10-20. Baseline: `2ae6544f96ad8662fadabd6d5cf373fd6931227d`.

## Repository findings

Remote `jellynada/guitar-boy-advance-expanded` was inspected with `git ls-remote`
and fetched. `foundation-audit-2026-10-20` and `mission-014-pause-resume` both
pointed to the baseline. Main was `6c4e63460fab10733d8ff011045ee246e7201952`;
develop was `56f6b7b243dfc710996336b99ac249806e666c85`. Both are ancestors of
the baseline (successful `merge-base --is-ancestor` checks). Implementation uses
a separate worktree on the designated foundation branch. No history rewrite,
merge, branch deletion, or default-branch change is needed. Private M014 files
remain in their existing directories outside this worktree.

This audit inspects source, rather than treating historical reports as new test
results. WORKING below describes implemented behavior backed by source/existing
regressions; the Mission 015 result record distinguishes tests actually rerun.
Hardware acceptance is not inferred.

## Subsystem assessment

| Subsystem | Classification | Source finding and remaining verification |
| --- | --- | --- |
| Memory/resources | NEEDS VERIFICATION | Fixed-size imported runtime/scoring/hold templates; 32 MiB cartridge guard (`tools/check_rom_size.py`). Chart size affects static RAM. Historical M014 Cream observations: 9,464 EWRAM bytes, 27,164 IWRAM payload bytes, 932 user-stack/40 IRQ-stack bytes touched. These are historical measurements, not exhaustive bounds; add CI ELF section budgets and retain hardware stack checks. |
| CPU/DMA/interrupts | NEEDS VERIFICATION | `scanline.cpp` double-buffers affine/blend tables, rearms DMA0/3 at VBlank, and records deadline misses. `pcmPlayback.cpp` uses Timer0 sample consumption, Timer1 refill IRQ, Timer2 cascade, Timer3 cost measurement, and bounded 16-byte FIFO writes. Historical Cream foreground peak 161,472 cycles and refill peak 1,408 cycles need physical confirmation. No new DMA/timer should be allocated without a resource review. |
| Audio/clock | WORKING | Two signed8 mono ROM streams at 16,384 Hz; integer hardware sample clock drives chart time. Explicit guitar gate/backing separation. No runtime compressed decoder. Strict common-backing emulator comparison has a documented failure; not solved by this mission. |
| ROM/assets | PARTIALLY IMPLEMENTED | Generated chart/audio plus original demo are linked into one ROM. Asset/profile/commit markers and final ROM-vs-ELF checks exist. No generic multi-song directory or streaming cartridge protocol. |
| Chart/MIDI/package parsing | PARTIALLY IMPLEMENTED | `song_package.py` bounds ZIP/folder reads, rejects unsafe paths/symlinks/encryption/unsupported compression and ambiguous chart/offset choices. `.chart`, bounded SMF type0/1 MIDI, song.ini, tempo changes and rational timing exist. Runtime adaptation deliberately accepts only compatible Easy lead-guitar lanes; no arbitrary remapping. Other instruments/difficulties are inspection data, not gameplay support. |
| Audio preparation | PARTIALLY IMPLEMENTED | Host FFmpeg handles OGG/MP3/WAV/OPUS; explicit stems, shared gain, pre-roll/tail, hashes and chart binding. `prepare_song.py` checks final note onset against audio length; full sustain-end alignment needs review. Host FFmpeg versions can change PCM. |
| General song builds | PARTIALLY IMPLEMENTED | Low-level preparation accepts packages, but official `build_profile.py` has public/Cream profiles. `release_common.validate_assets` hard-codes Cream 395 heads/78 holds/three selected stems. Keep those as fixture checks; add a separate generic profile/schema in Mission016. Metadata still contains historical Left/A/B and silence/no-tail descriptions although physical runtime is LEFT/B/A with sustains. Correct through versioned pipeline work, not gameplay rewrites. |
| Judgment/scoring/sustains | WORKING | Separate `noteJudgment.hpp`, `scoring.hpp`, `sustain.hpp` and host regressions. Hold bonus depends on actual hit phase; different input scripts need not have identical scores. Preserve rules. |
| Pause/resume/input | NEEDS VERIFICATION | `playTransport.hpp`, `physicalInput.hpp`, and main.cpp preserve clock/state, seed held frets, freeze holds and handle exit chords. PCM resume validates cascaded counters/FIFO fill and starts a fresh sample period (up to 61.04 microseconds phase boundary). Existing 21-case emulator driver; owner handheld acceptance remains pending. |
| Session/render boundaries | PARTIALLY IMPLEMENTED | Gameplay rules are headers, hardware playback and scanline services are separate, but scene/session/render transitions remain concentrated in main.cpp and use globals. No rewrite justified for CI delivery. |
| Reproducible builds | PARTIALLY IMPLEMENTED | Pinned Docker digest, immutable committed source export, generated source manifest, fresh outputs, isolated build profiles and asset hashes exist. ZIP timestamps currently vary; byte-identical repeated toolchain output is not established by a single build. Host tests need documented dependencies. |
| CI/GitHub delivery | MISSING | No `.github/workflows` in baseline. Existing `package_public.py` validates synthetic content and packages committed source, but no automated extracted-ROM execution/download receipt. `.github` is currently rejected by source allowlist. Add exact workflow allowlist, CI checks and versioned artifacts first. |
| QA | PARTIALLY IMPLEMENTED | `tests/check.sh`: host sanitizer programs plus Python importer/audio/release tests. Headless mGBA identity/gameplay/pause/graphics/audio tools exist, some tied to a specific container name. Integrate portable identity and pause smoke first; broader audio/graphics matrices remain separate gates. Never relax strict audio thresholds. |
| Windows/physical GBA | NEEDS VERIFICATION | Batch/PowerShell launcher wraps Python/WSL/Docker. Cloud execution does not verify Windows installation or real cartridges, buttons, sound, timing or analog output. No arbitrary ZIP/SD runtime loading is supported. |
| Licensing/provenance | BLOCKED | No root license found. Original demo MOD/chart/art remain in source and synthetic ROM. Synthetic imported music does not establish rights for inherited assets. Historical Cream delivery branches remain in remote history. No new private content or passwords may enter source/artifacts. Public release requires owner publication approval plus inherited-asset clearance. |

## Prioritized backlog and acceptance

| Priority / mission | Dependency and risk | Measurable acceptance |
| --- | --- | --- |
| P0 / 015 CI and delivery | Existing official source/export guards; `.github` must not become a broad exemption. Public publication approval and provenance review gate release. | Host checks; clean pinned public build; exact manifest/source/ROM/ZIP hashes; safe extraction; matching ELF and identity; emulator pause/resume; versioned CI artifact only after success. Actual Actions run and real download verified separately after approved push. |
| P0 / 015 approved prerelease | CI success, owner approval, inherited asset review. Releases on public repository expose contents. | Publish approved development prerelease using exact verified artifact, anonymously download it, compare checksum and archive contents; record URL/receipt. Stable release is separately approved. |
| P1 / 016 generic pipeline | Preserve existing normalized/adapted/audio schemas and strict compatibility checks; avoid Cream regression changes. | Versioned package manifest separates source, normalized events, stems, runtime controls; at least two distinct supported synthetic packages build with no source edits; malformed inputs fail with reports; onset and sustain-end alignment tested. |
| P1 / 017 capacity | Existing dual-stream mixer/gating and pause sample continuity. Decoder changes risk IRQ deadlines. | Benchmark one block decoder with actual ARM CPU/RAM/ROM measurements, full-song exact clock and regression evidence; keep current PCM until criteria pass. |
| P1 / 018 runtime | Generic song data and measured budgets. Risk of unnecessary scene rewrites. | Explicit platform/audio/input/session/render ownership, bounded workloads, no gameplay changes, all existing regressions plus transition coverage. |
| P2 / 019 Windows | Stable CLI/schema and real Windows machine. | Owner independently imports synthetic packages and builds/plays without editing source; errors actionable; platform results recorded. |
| P0 acceptance / 020 | Above plus owner hardware and licensing gates. | Full tests, known failure disposition, Windows and GBA test reports, download receipt and approved release. Passing cloud tests alone never closes acceptance. |

## Audio capacity investigation (estimates, not benchmarks)

Current stereo-role separation is two mono signed8 streams: 32,768 bytes/second,
about 8.35 MiB for 267.27 seconds before pre-roll/tail/guard and engine bytes.
A 32 MiB conventional cartridge cannot hold a substantial four-minute library.

| Candidate | Approximate storage versus current PCM | Cost/risk to measure |
| --- | --- | --- |
| Two-stream 4-bit block ADPCM | About 1/2, plus block headers | Decode both streams into bounded RAM ahead of FIFO; preserve independent guitar gating, sample counts and paused decoder state. CPU/IRQ headroom and quality unknown. Best first benchmark candidate. |
| Lower-rate PCM (8,192 Hz) | About 1/2 | Low decoder cost but reduced bandwidth; clock constants, chart alignment and output quality need testing. Not a free quality-preserving change. |
| Aggressive 2-bit/predictive codecs | Potentially 1/4 plus headers | Quantization artifacts, predictor drift, block boundaries and CPU costs unmeasured. Do not choose from ratio alone. |
| Single mixed stream | About 1/2 | Loses reactive guitar separation; unsuitable without a different verified gameplay/audio strategy. |
| Tracker/synth arrangements | Content dependent, potentially much smaller | Does not preserve arbitrary user recording; useful for original licensed content only. |
| Cartridge-specific external streaming | Removes conventional ROM bound | Requires explicit flashcart protocol and latency/error handling; not portable GBA support and not promised. |

For an ADPCM experiment, target unchanged 16,384 Hz dual roles, at least 1.8x
net compression, bounded decode buffers, no new DMA/timer allocation, no audio
underruns, unchanged source-sample/chart timing across pauses and all existing
regressions. Establish baseline worst-case foreground/refill/decode budgets
before approving runtime integration. Plan capacity as available ROM bytes /
measured per-song encoded bytes; reserve engine/assets/table overhead first.

## First controlled implementation

1. Allow only the reviewed `.github/workflows/foundation.yml` source path; retain
   all private/generated/payload/symlink guards and add negative regressions.
2. Add pull-request/manual CI for host checks and official synthetic build,
   explicit versioned package/checksums, safe extraction and existing headless
   identity/pause execution. Keep runtime M014 identity: this slice changes build
   infrastructure, not the engine generation or gameplay.
3. Supply a reusable package verifier and emulator runner, usable locally and in
   CI, and document GitHub Actions artifact versus approved Release downloads.
4. Test and commit on the foundation branch. Stop before public push/publication
   for owner authorization. No stable tag, release, merge or default change.

No private recording, new gameplay, complete library, or speculative refactor is
part of this slice. Download delivery remains unverified until a real GitHub
artifact is published and retrieved successfully.
