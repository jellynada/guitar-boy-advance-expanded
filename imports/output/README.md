The importer creates a folder here for each chart, with `report.txt`,
`report.json`, `song.json` and `song_data.hpp`. These generated files are ignored
by Git. A failed re-import removes its old song JSON/header so stale assets
cannot appear to be a successful new import. Do not store hand-written files
under these generated filenames. The current GBA build does not read this folder.

Mission004 package reports use `packages/<input-name>/` by default, separate
from the preserved chart-only command. Read `report.txt` first. Normalized
`song.json` is preparation, not a new playable ROM.
