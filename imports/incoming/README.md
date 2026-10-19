Place a chart you are authorized to use here, then run from the project folder:

```text
python3 tools/import_chart.py
```

Only `.chart` files are read; audio is not imported or downloaded. Files in this
folder are ignored by Git to avoid accidentally redistributing community content.
Use the synthetic example in `tests/fixtures/charts` if you have no licensed chart.
See `docs/CHART_IMPORT_GUIDE.md` for a complete walkthrough.

Mission004 also accepts authorized song ZIPs/folders/MIDI here:
`python3 tools/import_song.py`. See `docs/SONG_PACKAGE_IMPORT.md`.
No imported community chart/audio should be committed publicly.
