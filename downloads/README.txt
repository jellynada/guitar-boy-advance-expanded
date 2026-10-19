MISSION 009 - START HERE

This public ROM contains ORIGINAL SYNTHETIC music, not Cream.

1. Extract All on Windows.
2. In mGBA choose File > Load ROM.
3. Open Guitar-Boy-Advance-Mission-009-Synthetic.gba.
4. Confirm M009 HOLDS and choose Imported Easy Test.
5. GBA lane controls, left to right: Left / A / B.

Hit the head, then hold long notes for bonus points. Release early without
losing combo or muting guitar. Wrong new presses still have their normal penalty.
At results: A or Start replays; B or Select returns to the mode selector.
Map GBA A/B to your preferred computer keys in mGBA settings.

The synthetic fixture has25heads and6genuine holds, including A+B together,
notes arriving during holds, and a deliberate same-lane overlap. Full scripted
play earns512points (470head +42hold bonus), with5completed/1retired early.

CREAM ROM
The real395-head/78-hold Cream build was successfully compiled and tested with
the complete267-second recording, results and replay. The mission restricts
public upload of the new Cream ROM. No private transfer destination is available.
Use BUILD_CREAM_ON_WINDOWS.md, or the full source guide in
 guitar-boy-advance-expanded/docs/SUSTAIN_GAMEPLAY.md .
The two build commands were exercised with the real ZIP and pinned Docker
compiler and reproduced the tested private ROM byte for byte.

Evidence:98Python tests plus C++ sanitizer checks, full-song real/synthetic
scoring/hold/display/audio/replay regressions, native screenshots and public logs.
No human Windows playing/listening or physical GBA test is claimed.
Existing perspective/fog/sprite glitches remain. Main is not merged.
Draft PR creation was attempted but the GitHub API returned Forbidden; no PR
was created. Use the source comparison for review.

Source revision: f589e62a225651c7bd8a39ad27f517e3890cd1fb
