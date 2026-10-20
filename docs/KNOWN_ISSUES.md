# Known issues — Mission013 review candidate

Owner reports successful Mission011 Windows/mGBA and physical-GBA playtests:
flicker gone, good music, working scoring/sustains/results/replay. These scoped
acceptance results do not certify every platform, timing margin or later build.
Source can be saved and integrated for development independently of stable-release
approval. Mission013 remaps imported Easy to LEFT/B/A. Its handheld acceptance is still pending;
older hardware feedback does not approve this build.

| ID | Priority | Status and evidence | Next action |
| --- | --- | --- | --- |
| GFX-010-001 | Resolved in exercised cases | Imported scanline repair d0b20dc; full M011 real0/16086 defective frames. Owner now confirms flicker gone in mGBA and on handheld. | Preserve frame/DMA regressions; do not redesign projection. |
| QA-010-004 | P1 stable compatibility gate | M011 had two additional strict >0.999 common-backing comparisons failing in unmodified mGBA0.10.1. Exact digital samples were correct; experimental emulator late-event correction explained failures. | M013 all primary models and three strict comparisons now pass unchanged limits (scoring min0.9999964, wrong0.9999529). No emulator correction used. This build-dependent pass is not a general emulator fix; retain cross-build/version validation and historical failures. |
| HW-010-008 | P1 validation risk | Owner reports game runs very well on actual GBA. M011 emulator minimum final DMA-write margin13cycles; actual hardware margin and stack high-water remain unmeasured. | Targeted hardware measurements/long sessions; no comprehensive certification claimed. |
| BUILD-012-001 | P1 platform validation | WSL/Python/Docker build chain is exercised on Linux; actual Windows double-click GUI execution is not available in this cloud machine. | Owner follows WINDOWS_PRIVATE_BUILD and reports visible errors; no claim of a performed Windows launcher test. |
| CTRL-012-001 | P2 confirmed physical usability | M013 now maps LEFT/B/A with matching receptors/diagnostics; Original stays LEFT/RIGHT/A/B. | Automated checks pass; owner must personally test this new mapping on handheld before acceptance. |
| QA-010-005 | P2 platform dependent | Some keyboards cannot send all chord keys; injected emulator keys cannot establish real keyboard rollover. | Use INPUT / CHORD TEST, alternate mappings or controller; physical GBA feedback is scoped. |
| GFX-010-002 | P2 inherited cosmetic | Distance fog retains abrupt bands from original coefficients. | Later visual review; not a timing fix or M013 feature. |
| GFX-010-003 | P2 observation risk | Earlier popping/obscuration report was not fully reproduced independently; owner now reports good overall operation and flicker fixed. | If it recurs, capture mode/time/version; do not invent a speculative patch. |
| REL-010-006 | Review gate | Main remains immutable historical6c4e634; source integration proposal and develop are separate from stable release. | Explicit owner approval required before main merge; never merge download branches. |
| REL-010-007 | P1 provenance gate | Inherited music/art/chart/code and historical public Cream downloads (including M011) require separate redistribution review. No repo-wide LICENSE found. | Preserve history and attribution. M013 public review ZIP excludes Cream. The separately authorized AES download contains ciphertext only, with its key outside GitHub. Private launcher never uploads. |
| CAP-012-001 | Design constraint | Roughly9MB per four-minute dual-PCM song cannot scale to ten songs in32MiB. | Future codec/storage feasibility study, no mixer/codec changes now. |

No new reproduced crash is asserted here. Passing exercised cases does not prove
all undefined behavior, hardware limits or historical licensing questions solved.
Future physical-order controls, sustain feedback and audio budget work are recorded
in DESIGN_BACKLOG.md and are deliberately unimplemented.

## Mission013 boundaries

No active failing ordinary waveform check was observed in the current M013
matrix. Prior M011/M012 failures remain recorded; do not claim the underlying
emulator late-event issue repaired. Actual Windows launcher and physical
stack/DMA margins remain unmeasured by the agent. Future Hard Up/Down alias
fixtures are tests, not a playable difficulty. Historical adapted JSON includes
obsolete button annotations; runtime logical IDs, gameControls.hpp, build manifest
and visible labels define current physical mapping (see PHYSICAL_INPUT.md).
Owner M013 acceptance: **pending**, including LEFT/B/A comfort, chords and holds.
