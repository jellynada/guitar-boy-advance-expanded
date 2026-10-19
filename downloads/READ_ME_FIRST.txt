MISSION 004 — START HERE

The included ROM is the unchanged working demo, not Sunshine of Your Love.
1. Install mGBA from https://mgba.io/downloads.html.
2. Unzip this bundle. In mGBA choose File > Load ROM and select
   guitar-boy-advance-mission-004.gba.
3. Map GBA Left / Right / A / B to convenient keyboard keys such as D/F/J/K.

TRY IMPORTING (Python3.10+, no extra packages):
Open a terminal in this extracted folder and run:
python3 tools/import_song.py tests/fixtures/midi
Windows can replace python3 with py -3.
Open imports/output/packages/midi/report.txt. Synthetic example has no audio.

YOUR PRIVATE PACKAGE:
python3 tools/import_song.py "Cream (WaveGroup) - Sunshine of Your Love (Neversoft).zip"
That actual package was unavailable here. No target-song compatibility claimed.
The importer discovers notes.mid/song.ini and audio if present, but does not make
new songs playable yet. Keep third-party charts/audio private.

Read README.md and docs/SONG_PACKAGE_IMPORT.md for choices and explanations.
SOURCE_COMMIT.txt identifies source; source-changes.patch is against Mission003.
PULL_REQUEST.md is prepared, but GitHub API returned Forbidden: no PR opened.
Review page:
https://github.com/jellynada/guitar-boy-advance-expanded/compare/mission-003-chart-importer...mission-004-universal-import
No automatic merge. The download branch must not be merged into main.

Build instructions require the full source checkout; this is a standalone import
review bundle, not every original game build asset. Evidence logs show actual
66Python tests, gameplay sanitizers, native/Docker builds and three mGBA runs.
No manual listening/hand play is claimed. Full details:docs/MISSION_004_RESULTS.md.
