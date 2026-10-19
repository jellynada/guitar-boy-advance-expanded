MISSION 005 — START HERE

1. Install mGBA: https://mgba.io/downloads.html . Unzip this bundle.
2. Load guitar-boy-advance-mission-005.gba.
3. Use GBA Up/Down, then A or Start to choose a mode.
   Original Demo: Left/Right/A/B, existing music.
   Imported Easy Test: Left/A/B, original synthetic25-note chart, SILENT.
4. Start+Select returns to the selector and restarts a chosen mode cleanly.
   Configure GBA button assignments in mGBA settings (for example D/F/J/K).

The actual owner-supplied Cream/WaveGroup395-note Easy chart passed PRIVATE
all-hit/all-miss emulator tests. Its audio is not decoded or played. That chart,
its normalized/adapted note files and its chart-containing ROM are NOT published
in this bundle. This is the synthetic review build, not the Cream chart ROM.

This ZIP includes COMPLETE TRACKED SOURCE and original build assets (no Git
knowledge required). Windows11 preparation/build guide:
docs/GBA_CHART_ADAPTATION.md
You can prepare your private song with:
python3 tools/prepare_easy.py "path/to/song.zip"
Then, in Ubuntu/WSL with Docker Desktop running:
bash scripts/build-docker.sh "IMPORTED_HEADER=imports/output/easy-runtime/imported_chart.hpp"
Choose Imported Easy Test in the resulting guitar-boy-advance-expanded.gba.
No Python/C++ editing. Read the guide for installing WSL/Docker/Python first.

Evidence:75Python tests plus C++ sanitizer checks; real native and clean pinned
Docker builds;7automated gameplay scenarios (original3,synthetic2,private real2).
Imported scenarios also test repeated original/imported resets and silence.
No actual imported recording synchronization, manual listening/hand play or
hardware/latency calibration is claimed.

SOURCE_COMMIT.txt identifies the exact source. PULL_REQUEST.md is prepared.
GitHub rejected PR creation with Forbidden; no PR was opened and nothing merged.
Review:
https://github.com/jellynada/guitar-boy-advance-expanded/compare/mission-004-universal-import...mission-005-first-playable-import
The download branch must not be merged into main. Original asset permissions
are not newly established; keep third-party charts/audio private.
