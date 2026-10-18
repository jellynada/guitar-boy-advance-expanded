MISSION 002 — DOWNLOAD AND PLAY

1. Install mGBA from https://mgba.io/downloads.html.
2. Unzip this bundle. In mGBA choose File > Load ROM and open:
   guitar-boy-advance-mission-002.gba
3. In mGBA keyboard/controller settings, map the GBA buttons:
   LEFT lane (green): D-pad Left
   Second lane (red): D-pad Right
   Third lane (yellow): A
   RIGHT lane (blue): B
   Suggested computer keys: D, F, J, K in that same order.
4. The song starts automatically. Press a fresh button as a note reaches its
   circle. H counts hits, M counts misses. PERFECT/GOOD/MISS is the latest
   result; WRONG briefly flags incorrect presses. Holding is not a new press.
5. Let notes pass: M should increase. Hit a note: H should increase only once.
   By the end, H + M should equal 699. Reset/reload in mGBA to replay.

Your previous Mission 001 download and the main branch have not been changed.
This version uses the same song, highway and artwork. It adds reliable note
judgments, feedback and your requested controls, not a new scoring/audio system.
The music still loops without restarting the chart. A physical D-pad cannot
normally hold Left and Right together; the existing chart has no chords.

Automated host and mGBA tests passed. No person manually played or listened to
this Mission 002 version during development; please judge play feel and sync.
Detailed rules, results and known limitations are in the docs folder.

Source and review:
https://github.com/jellynada/guitar-boy-advance-expanded/tree/mission-002-note-judgment
https://github.com/jellynada/guitar-boy-advance-expanded/compare/mission-001-reproducible-build...mission-002-note-judgment
The prepared PR description is PULL_REQUEST.md. Automatic PR creation was
blocked by GitHub's API; the comparison is available without merging anything.
