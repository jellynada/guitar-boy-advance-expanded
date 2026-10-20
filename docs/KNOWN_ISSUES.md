# Known issues — Mission012 development baseline

Owner reports successful Mission011 Windows/mGBA and physical-GBA playtests:
flicker gone, good music, working scoring/sustains/results/replay. These scoped
acceptance results do not certify every platform, timing margin or later build.
Source can be saved and integrated for development independently of stable-release
approval. Mission012 changes building/identity only, not gameplay.

| ID | Priority | Status and evidence | Next action |
| --- | --- | --- | --- |
| GFX-010-001 | Resolved in exercised cases | Imported scanline repair d0b20dc; full M011 real0/16086 defective frames. Owner now confirms flicker gone in mGBA and on handheld. | Preserve frame/DMA regressions; do not redesign projection. |
| QA-010-004 | P1 stable compatibility gate | M011 had two additional strict >0.999 common-backing comparisons failing in unmodified mGBA0.10.1. Exact digital samples were correct; experimental emulator late-event correction explained failures. | Keep original thresholds and fresh M012 observations in MISSION_012_BUILD_FOUNDATION; no emulator correction used for normal acceptance. Owner says audio sounds good; that does not close the numerical gate. |
| HW-010-008 | P1 validation risk | Owner reports game runs very well on actual GBA. M011 emulator minimum final DMA-write margin13cycles; actual hardware margin and stack high-water remain unmeasured. | Targeted hardware measurements/long sessions; no comprehensive certification claimed. |
| BUILD-012-001 | P1 platform validation | WSL/Python/Docker build chain is exercised on Linux; actual Windows double-click GUI execution is not available in this cloud machine. | Owner follows WINDOWS_PRIVATE_BUILD and reports visible errors; no claim of a performed Windows launcher test. |
| CTRL-012-001 | P2 confirmed physical usability | Current Easy Left/A/B places A before physically nearer B. | Future explicitly scoped Left/B/A remap; no mapping changes in M012. See DESIGN_BACKLOG. |
| QA-010-005 | P2 platform dependent | Some keyboards cannot send all chord keys; injected emulator keys cannot establish real keyboard rollover. | Use INPUT / CHORD TEST, alternate mappings or controller; physical GBA feedback is scoped. |
| GFX-010-002 | P2 inherited cosmetic | Distance fog retains abrupt bands from original coefficients. | Later visual review; not a timing fix or M012 feature. |
| GFX-010-003 | P2 observation risk | Earlier popping/obscuration report was not fully reproduced independently; owner now reports good overall operation and flicker fixed. | If it recurs, capture mode/time/version; do not invent a speculative patch. |
| REL-010-006 | Review gate | Main remains immutable historical6c4e634; source integration proposal and develop are separate from stable release. | Explicit owner approval required before main merge; never merge download branches. |
| REL-010-007 | P1 provenance gate | Inherited music/art/chart/code and historical public Cream downloads (including M011) require separate redistribution review. No repo-wide LICENSE found. | Preserve history and attribution. M012 public packages exclude new Cream data; private launcher never uploads. |
| CAP-012-001 | Design constraint | Roughly9MB per four-minute dual-PCM song cannot scale to ten songs in32MiB. | Future codec/storage feasibility study, no mixer/codec changes now. |

No new reproduced crash is asserted here. Passing exercised cases does not prove
all undefined behavior, hardware limits or historical licensing questions solved.
Future physical-order controls, sustain feedback and audio budget work are recorded
in DESIGN_BACKLOG.md and are deliberately unimplemented.
