# Known issues — Mission 010

This is a review candidate, **not an owner-accepted stable release**. P0 means
blocking crash/timing/data failure; P1 affects gameplay or release verification;
P2 is cosmetic; P3 is future work. No reproduced P0 remains in the exercised cases.
This is not a claim that every owner-visible defect has been reproduced.

| ID | Severity | Description / expected versus actual | Reproduction | Status / evidence / acceptance |
| --- | --- | --- | --- | --- |
| GFX-010-001 | P2 in captured cases; escalate to P1 if notes become obscured | Highway should have continuous scanlines; thin displaced horizontal floor marks appear during PCM audio. | Imported synthetic audio, about 4 seconds into the mode. Compare `synthetic-sustain-perfect.tails-240.png` with `silent-perfect.tails-240.png`. | Reproduced, deferred. Isolated IRQ probe counted 12,994 late HBlank entries /215,553 calls with audio, versus 1/200,878 silent. Counts include navigation and have instrumentation overhead. FIFO ISR maxima exceed one scanline; evidence supports delayed affine updates. No proof that all owner glitches share this cause. A DMA/precomputed-affine repair needs a separately validated timing change. No fix commit. Owner: report exact song time and whether a head is hidden. |
| GFX-010-002 | P2 | Distant highway/fog has abrupt bands rather than smooth distance fading. | Look at the horizon in native gameplay screenshots. | Reproduced, original blending design. Deferred; no renderer redesign. Owner: confirm whether readability is affected. |
| GFX-010-003 | P1 if reproduced | Owner reports popping/obscured graphics; expected stable visible note heads. | Owner-specific passage/emulator settings still needed. | Not fully reproduced. Audited OAM, VRAM, priorities, affine IDs, clipping; sampled heads/tails stay aligned and bounded. Per-frame OAM/VRAM writes and interrupt contention remain risks; no speculative patch. Owner: supply a short recording or screenshot, mode, approximate song time and mGBA version. |
| QA-010-004 | P1, blocks stable promotion | Reactive mixed hit/miss waveform must satisfy existing >0.94 correlation check. One fade-down window gives 0.909975 at 232.665039s; timing residual -0.671387ms remains within 1ms. | Run full Cream `reactive` scenario then `tests/analyze_reactive.py` with the reference times in QA_TEST_PLAN. | OPEN. Baseline M009 reactive passes; current head/gate events match at the failing event, PCM/gate source is unchanged, and seven other primary real waveform models pass. Sub-sample alignment probes did not resolve it; cause is not established. No threshold relaxed and no audio fix claimed. Additional strict optional common-backing comparison also fails at 46.137634s (0.998523 versus >0.999); keep that evidence separate. Needs sample/PWM-level diagnosis and owner listening. No fix commit. |
| QA-010-005 | P1 | mGBA input should include every physical key; some PC keyboards drop simultaneous keys. | Run input diagnostic with Left+A, Left+B, A+B, all three. | Hardware-dependent, not reproduced through injected mGBA keys. Try alternative key mappings or controller. Owner acceptance pending. |
| REL-010-006 | P1 | Stable source integration should be reviewed, reproducible and free of download artifacts. Main remains historical. | Inspect branches and RELEASE_PROCESS. | Merge-ready source proposal only; integration blocked on QA-010-004, owner acceptance and permissions review. No automatic merge, tag, deletion or history rewrite. |
| REL-010-007 | P1 | New Cream playtest delivery needs a supported private destination or established third-party redistribution rights. | Chat private artifact links previously failed. | Current real ROM built/tested locally; no working private uploader. Verified local Windows/WSL build workflow is the fallback. Historical M006–009 public Cream ROMs require separate permissions review; owner upload requests are not proof of third-party rights. No new M010 Cream publication. |
| HW-010-008 | P1 release risk | Physical GBA frame/audio/memory safety must be checked on hardware. | Play full song/replay on actual GBA and supported flash cartridge. | Not performed. Emulator profiling does not establish hardware performance; stack high-water usage not measured. |

No existing graphics fix is claimed in Mission 010. The implemented changes add
isolated diagnostics and stronger QA/build safeguards; graphics evidence is
preserved rather than hidden by a broad rewrite.

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
