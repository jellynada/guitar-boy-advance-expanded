MISSION 007 — START HERE

This public ROM is the ORIGINAL SYNTHETIC two-track exercise, not Cream.
1. Install mGBA from https://mgba.io/downloads.html .
2. Unzip and use File > Load ROM to open guitar-boy-advance-mission-007.gba.
3. Up/Down chooses Imported Easy Test; A or Start begins.
4. Play with GBA Left / A / B, mapped to convenient computer keys.
5. Let a note pass: after its late window, the bright lead disappears, while bass/percussion continue. GUITAR MUTED is displayed.
6. Hit another note: the lead returns and GUITAR ON is displayed.
7. A wrong active button mutes again. Waiting never restores it.
8. Start+Select returns to the selector; replay starts with guitar ON.
Original Demo retains Left / Right / A / B and the original music.

No Cream audio, chart or reactive Cream ROM is in this download.
The real song was tested privately, including complete395-note all-hit/no-input/hit-miss-hit/wrong-hit scenarios. This session has no working private attachment tool. Follow guitar-boy-advance-expanded/docs/REACTIVE_GUITAR_AUDIO.md to reproduce that ROM privately with your existing ZIP on Windows11 using WSL/Docker/FFmpeg. No source edits or Git commands are needed.

The full source folder is guitar-boy-advance-expanded inside this bundle.
Source: mission-007-reactive-guitar-audio. Main is not merged.
Review: https://github.com/jellynada/guitar-boy-advance-expanded/compare/mission-006-audio-sync...mission-007-reactive-guitar-audio
GitHub draft PR creation returned Forbidden; no PR was created. Prepared description included.

Checks:92Python tests plus C++ sanitizer checks; identical native and clean Docker ROMs; full synthetic/private captured waveform validation, true-zero gate arithmetic, backing-only/recovery/fault/replay tests; original699-note regressions. Docs contain exact measurements and limitations. No human audition or physical GBA test claimed. Actual instrument separation still needs listening confirmation.
