# Mission 008 HUD and completion hotfix

The owner reported an unreadable/missing numerical score and an empty highway
at song end. This supersedes the previous automated acceptance claim. The owner
explicitly authorized a public Cream ROM download in the current request;
the attachment's earlier private-only delivery instruction is superseded.
Main is not merged. Work is on `mission-008-hotfix-hud-completion`.

## Findings and limits of the diagnosis

The earlier exact Mission 008 Cream ROM and saved final composite mGBA images
already contain a score HUD and complete results. The hotfix investigation has
not reproduced the owner's missing results/softlock in this Linux mGBA core.
Consequently, there is **no confirmed root cause for the reported freeze**.
It would be inaccurate to claim a particular BG priority or audio EOF bug caused
it. Windows mGBA version and the exact ROM loaded may help establish that cause.

A concrete readability weakness is confirmed: the old existing font has small,
sparse glyphs, abbreviated S/C/X labels and only two HUD rows at the screen edge.
A screenshot containing text is insufficient evidence that the owner can read it.

The existing BG0 HUD shares priority zero with BG1's black horizon mask. BG0
wins equal-priority ties, and BG1's alpha blending affects the existing highway,
not BG0. No priority defect was observed in the composite screenshots.
The earlier tests checked results map entries and internal scores but did not
assert the composed pixels. Screenshots existed, but their existence was not a
strong enough acceptance gate. That gap allowed an overconfident earlier report.

The completion path defers an EOF observed after an earlier clock snapshot.
Normally this catches up on the next frame. Its wait had no bound. This hotfix
bounds that particular wait to 120 foreground frames (about two seconds), then
shows DATA ERROR / CLOCK DID NOT SETTLE. This is defensive handling, **not proof
that this wait caused the owner's incident**. Already-ended unresolved notes
and incoherent statistics retain error outcomes, never fabricated hits/misses.

## Changes

- Use the existing Tonc library's bundled system font, expanded to 4bpp BG tiles,
  with a dedicated white palette bank. No third-party replacement art was added.
- Three rows, within the existing top mask: SCORE, COMBO, MULT, temporary judgment
  and guitar status. The numerical values remain visible between judgments.
- Use the same clearer font on results/error screens.
- Label the selector `M008 HOTFIX 1` so the owner can identify this build.
- Add a bounded EOF snapshot diagnostic and visible reasons: CLOCK DID NOT
  SETTLE, UNRESOLVED NOTES, STATS MISMATCH. Audio faults still show AUDIO ERROR.
- Keep scoring, event order, judgment windows, chart, guitar gate, audio rate,
  samples, perspective and controls unchanged.

## Acceptance checks

`tests/audio_emulator.c` now compares the **final composed framebuffer pixels**
to the expected system-font glyphs at the displayed score/combo/multiplier.
Checks run repeatedly while values have been stable for several frames, including
quiet periods. It checks temporary judgment lettering when sampled during its
visible interval. It verifies the composed results heading, all statistic labels
and numerical values, accuracy, awards, and replay/menu instructions. Replay is
checked for reset visible score and newly advancing audio, rather than only a
reset flag. Saved screenshots are native 240x160, without scaling or enhancement.

Negative tests deliberately hide BG0 or the results BG; the pixel assertions
must fail even while internal scores/maps remain correct.

An additional **test harness bug**, not a gameplay clock defect, was discovered
while rerunning waveform analysis: sampling stopped Timer1 before audio started
could fabricate a 64-second wrap in the independent capture clock. The capture
harness now starts its hardware epoch only after playback begins. The first
waveform-analysis attempt failed on that fabricated offset; it was investigated,
not waived. The actual game clock and playback code were not changed.

Build and test evidence, downloadable file hashes, and any remaining checks are
recorded in `MISSION_008_HOTFIX_RESULTS.md` alongside the native screenshots.

## Windows 11 playtest

Download the hotfix ZIP from the delivery link, right-click and Extract All.
In mGBA choose File > Load ROM and open
`Sunshine-of-Your-Love-Mission-008-Hotfix.gba`.
Confirm the selector says **M008 HOTFIX 1**. Choose **Imported Easy Test**.
Use GBA **Left / A / B** from left to right; configure PC keys in mGBA's settings.
The original demo retains Left / Right / A / B.

Watch SCORE, COMBO and MULT. Wait through the entire recording (roughly 4m30s
including lead-in and tail). On results, A or Start replays; B or Select returns
to selection. Load the new ROM directly rather than restoring an old save state.
Manual Windows playing/listening and physical hardware remain owner checks.
