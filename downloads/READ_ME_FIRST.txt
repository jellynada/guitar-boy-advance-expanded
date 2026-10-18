MISSION 003 — CHART IMPORT TOOLS AND WORKING DEMO

The game ROM is byte-for-byte identical to Mission 002: same song, note
judgments, highway and Left / Right / A / B controls. New work is the standalone
chart importer, not new audio or gameplay. Main and previous downloads are unchanged.

TO TRY THE IMPORTER
1. Install Python 3.10+ from https://www.python.org/downloads/ if needed.
2. Unzip the bundle. On Windows, open this folder in File Explorer, type cmd
   in its address bar and press Enter. On macOS, open Terminal, type cd followed
   by a space, drag this folder into Terminal, then press Enter.
3. Run:
   python3 tools/import_chart.py tests/fixtures/charts/tempo_changes.chart
   On Windows you can use py -3 instead of python3.
4. Open imports/output/tempo_changes/report.txt. It explains the synthetic
   test chart, independent difficulties and unsupported gameplay features.
5. To inspect a chart you are authorized to use, place its .chart file in
   imports/incoming and run:
   python3 tools/import_chart.py

Successful import means PREPARED, NOT PLAYABLE. The current game does not read
these new tables yet. No audio is downloaded or opened. No authorized Sunshine
of Your Love chart was provided; nothing was fabricated or substituted.
See docs/CHART_IMPORT_GUIDE.md and docs/SONG_DATA_ARCHITECTURE.md.

TO PLAY THE UNCHANGED DEMO
Install mGBA from https://mgba.io/downloads.html. Choose File > Load ROM and open
  guitar-boy-advance-mission-003.gba
Map GBA D-pad Left / D-pad Right / A / B to convenient computer keys (for example
D / F / J / K). Reset/reload to replay; music loops without restarting the chart.
This task used automated mGBA testing, not a human listening/playthrough test.

This bundle includes standalone import tools, synthetic examples, reports,
logs, source patch and the ROM. Full game source/build assets are available at:
https://github.com/jellynada/guitar-boy-advance-expanded/tree/mission-003-chart-importer
Full development builds/tests require that complete source checkout and toolchain.

Review comparison (main was not merged):
https://github.com/jellynada/guitar-boy-advance-expanded/compare/mission-002-note-judgment...mission-003-chart-importer
Automatic PR creation was blocked by GitHub's API. PULL_REQUEST.md contains the
prepared description. No GitHub knowledge is required to try the tools or ROM.
