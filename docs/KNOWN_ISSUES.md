# Known issues — Mission 011

Outcome B: the imported scanline repair is verified; strict ordinary-emulator audio comparisons and owner acceptance remain open. This is **not an owner-accepted stable release**. P0 means
blocking crash/timing/data failure; P1 affects gameplay or release verification;
P2 is cosmetic; P3 is future work. No reproduced P0 remains in the exercised cases.
This is not a claim that every owner-visible defect has been reproduced.

| ID | Severity | Description / expected versus actual | Reproduction | Status / evidence / acceptance |
| --- | --- | --- | --- | --- |
| GFX-010-001 | P1 owner-confirmed; engine repair verified | Imported highway previously showed displaced pink/brown horizontal lines while Original stayed clean. | M010 actual Cream or synthetic PCM gameplay; native before/after sequences in screenshots/mission011. | Repaired by `d0b20dc`: imported-only double-buffered DMA affine/fog tables, hardware-polled VBlank rearm. Full Cream before16085/16085 flagged frames; after0/16086. Zero late X/Y/blend writes, zero rearm misses. No blanket renderer redesign. Windows/physical owner confirmation pending. |
| GFX-010-002 | P2 | Distant highway/fog has abrupt bands rather than smooth distance fading. | Look at the horizon in native gameplay screenshots. | Reproduced, original blending design. Deferred; no renderer redesign. Owner: confirm whether readability is affected. |
| GFX-010-003 | P1 if reproduced | Owner reports popping/obscured graphics; expected stable visible note heads. | Owner-specific passage/emulator settings still needed. | Not fully reproduced. Audited OAM, VRAM, priorities, affine IDs, clipping; sampled heads/tails stay aligned and bounded. Per-frame OAM/VRAM writes and interrupt contention remain risks; no speculative patch. Owner: supply a short recording or screenshot, mode, approximate song time and mGBA version. |
| QA-010-004 | P1 release-validation gate | Digital mixing is correct; mGBA PWM slot selection mishandles late FIFO events. Original M010232.665s primary failure reproduced exactly. Current M011 eight primary models pass, but ordinary strict backing comparisons fail at135.875s/scoring and128.039s/wrong. | Unmodified mGBA0.10.1 full real captures and unchanged >0.999 optional common-backing comparison. | Cause established by zero-mismatch FIFO data and emulator-only lateness correction with identical game events/clocks. Experimental correction passes both strict comparisons; it is not shipped or used for ordinary acceptance. No thresholds relaxed. Raw emulator compatibility remains OPEN; stable promotion blocked, owner listening pending. See MISSION_011_AUDIO_GRAPHICS. |
| QA-010-005 | P1 | mGBA input should include every physical key; some PC keyboards drop simultaneous keys. | Run input diagnostic with Left+A, Left+B, A+B, all three. | Hardware-dependent, not reproduced through injected mGBA keys. Try alternative key mappings or controller. Owner acceptance pending. |
| REL-010-006 | P1 release risk | Main remains historical; accepted source must eventually be integrated under owner approval. | Inspect source versus download branches. | Mission011 excludes consolidation. No merge/tag/default-branch change/history rewrite. Prior proposal remains historical; current integration is not recommended before audio/platform and owner acceptance gates. |
| REL-010-007 | P1 delivery/permissions risk | Real playtest needs a supported private destination or established redistribution permission. | Earlier private chat links failed. | M011 actual Cream ROM built and reproduced; no supported private uploader. Exact Windows/WSL local workflow is verified in Linux. No new Cream upload. Historical public M006–009 binaries/original-demo assets still need separate rights review. |
| HW-010-008 | P1 release risk | Physical GBA frame/audio/memory safety must be checked on hardware. | Play full song/replay on actual GBA and supported flash cartridge. | Not performed. Emulator profiling does not establish hardware performance; stack high-water usage not measured. |

Mission011 repairs the imported scanline transport, preserving the projection, art,
normal note/tail drawing and existing fog coefficients. Other cosmetic/owner-specific
issues are not declared fixed. See MISSION_011_AUDIO_GRAPHICS.md for controlled
evidence, before/after sequences, exact audio failures and performance budgets.

## Player feedback / future design (P3, not implemented)

Perfect/Good is visible at the top for about 0.3 seconds, but does not identify a
specific lane. Receptor brightness reflects held buttons, not a successful
judgment. Tails retain lane color while approaching and active; they disappear
on release/completion, without explaining which occurred. Hold bonuses visibly
increase the score, but normal gameplay has no dedicated live hold/bonus label.
Combo/multiplier and GUITAR ON/MUTED are readable; guitar state is not conveyed
by a special lane animation. The diagnostic screen makes these distinctions
explicit without changing normal gameplay feedback.

Approved later polish: colored sustain head; dim lane-colored approaching tail;
white tail only during a valid active hold, with subtle glow/pulse; early release
breaks/removes remaining tail; ordinary completion with no celebration; clear
hit feedback close to the relevant fret. This is backlog only. No new animation,
white-tail system, difficulty, codec, song library, star power or health mechanic
is implemented here.
