# Mission 010 stabilization

## Pre-change baseline

Source: `mission-009-sustain-gameplay`, final review commit `f589e62a225651c7bd8a39ad27f517e3890cd1fb`.
Implementation: `85c637d4cf1c1029fbf8d2413ba0a63274ef234b`.
HUD/results hotfix: `71f0152c29d7008acd310808861643d5018e65a7`.
All mission source branch tips below were verified ancestors of this source.
Main remains `6c4e63460fab10733d8ff011045ee246e7201952`; initial repository commit `c27bd247a06561330a84773203772199fa210cdf`.
No download branch is used as a source base.

- `mission-001-reproducible-build`: `47d340e105ff3afb899b063683b2ee0dbc5b7943`
- `mission-002-note-judgment`: `533862124079a9dca1f84a6d88f54e40cde189cb`
- `mission-003-chart-importer`: `135a55c2a0de50a4c68610f1aeb288924508bb54`
- `mission-004-universal-import`: `1487532557a1e98b1c99c6628e5d65c291268cd2`
- `mission-005-first-playable-import`: `f23cb6b4039fec93811b80f557a85518b2f626d1`
- `mission-006-audio-sync`: `4fa9e6f8b2558a129075c9815c8bb2ac68e6421b`
- `mission-007-reactive-guitar-audio`: `90aaed9f2d7624258ff3485d6a0dc7858c126929`
- `mission-008-hotfix-hud-completion`: `71f0152c29d7008acd310808861643d5018e65a7`
- `mission-008-scoring-results`: `a6b36a22733992b274f352a190c9ec1d39547d1d`
- `mission-009-sustain-gameplay`: `f589e62a225651c7bd8a39ad27f517e3890cd1fb`

Download-only branches (do not merge):

- `mission-001-download`
- `mission-002-download`
- `mission-003-download`
- `mission-004-download`
- `mission-005-download`
- `mission-006-download`
- `mission-006-playtest-download`
- `mission-007-download`
- `mission-007-playtest-download`
- `mission-008-download`
- `mission-008-hotfix-download`
- `mission-008-playtest-download`
- `mission-009-download`
- `mission-009-playtest-download`

M009 public synthetic SHA256: `57ac5cb4201cd2f37e1124f27a89d05c115ff466cd9cea8e9d25748ea7a4e264`; 807,776 bytes.
M009 Cream SHA256: `e2e5a9740e7b75efbb70b0ba8e37a1fabdf41873932b4e50482290340336d214`; 9,171,164 bytes.

GCC ARM 16.1.0, host FFmpeg 7.1.5, mGBA 0.10.1 Debian library. Pinned Docker toolchain in scripts/build-docker.sh. Prior host baseline: 98 Python tests plus C++ sanitizer programs. Prior emulator maximum foreground 170,176 cycles (60.58% of frame), tail strips 11 real /31 synthetic, refill max 1,344 cycles, zero ordinary underruns. Linked IWRAM 26,516/26,096 bytes, EWRAM 3,464/3,096 private/synthetic, before linker padding/stack.

Graphics baseline: horizon/fog bands, horizontal scanline seams and possible sprite popping; these were previously documented limitations, not all owner-visible symptoms reproduced. Current native frames and full-song baseline runs are captured before implementation.

Permissions audit: source tracks charts/careless.chart, original graphics and the original soundbank source (inspect music assets and provenance before wider redistribution). Historical download branches publish embedded Cream recording/chart in ROMs for M006–009; owner upload authorization is recorded in chat, but third-party redistribution rights are not established by that request. This needs a separate permissions review. Private generated chart/audio and Cream.zip remain ignored; ignore rules do not remove previously published history. No history rewriting or removal is performed. Mission010 public additions will be synthetic only.
