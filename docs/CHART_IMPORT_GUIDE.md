> Mission 004: this page describes the preserved chart-only command. For MIDI,
> ZIPs, folders, INI metadata and audio discovery use [SONG_PACKAGE_IMPORT.md](SONG_PACKAGE_IMPORT.md).
> Limitations below refer to the old command, not the new package inspector.

# Importing community charts — Mission 003

A `.chart` file is a text description of where notes belong in a song. It is
**not music**: it contains beat positions, tempos, note lanes, difficulty tracks,
and sometimes filenames pointing to separate recordings. Importing it does not
supply audio or permission to use that audio.

Mission 003 prepares and checks these files on your computer. It deliberately
**does not replace the working demo** or claim imported songs are playable yet.
The existing ROM still has its same 699 notes, music, graphics and Left/Right/A/B
controls. New three/five-lane screens and audio preparation are future tasks.

## First try: no community chart or programming required

1. Download and unzip the Mission 003 review bundle. It includes the importer,
   original synthetic examples, reports, documentation and the working demo ROM.
2. Install Python **3.10 or newer** from https://www.python.org/downloads/ if your
   computer does not already have Python 3. Windows offers a launcher called `py`;
   use `py -3` instead of `python3` in the commands below if needed.
3. Open a terminal in the extracted folder (or project folder). On Windows,
   open that folder in File Explorer, type `cmd` into its address bar and press
   Enter. On macOS, open Terminal, type `cd ` (including the space), drag the
   extracted folder into the window and press Enter. Then paste:

   ```text
   python3 tools/import_chart.py tests/fixtures/charts/tempo_changes.chart
   ```

4. Open `imports/output/tempo_changes/report.txt` in a text editor. The synthetic
   example contains four independent difficulty tracks, tempo changes, a sustain,
   special markers and a D-pad conflict so you can see what the warnings mean.
   It is original test data with no commercial song or audio.

You do **not** need the GBA compiler or to edit C++ to inspect a chart. Python's
standard library is sufficient; no package download or account is needed.

## Import a chart you are allowed to use

Create your own chart with [Moonscraper](https://github.com/FireFox2000000/Moonscraper-Chart-Editor)
or obtain permission from a community chart's creator. A listing on a chart
website, a song title or access to a download is not a redistribution license.
Keep the chart's provenance, author, license and permitted use with your records.

1. Put the authorized `.chart` file in `imports/incoming/`. Give it a normal name
   such as `my_song.chart`. Do not put audio there as part of this mission.
2. From the project/extracted-bundle folder run **one command**:

   ```text
   python3 tools/import_chart.py
   ```

3. Open `imports/output/my_song/report.txt`. Each input gets its own folder.
   Alternatively, inspect one file anywhere using a quoted path:

   ```text
   python3 tools/import_chart.py "imports/incoming/My Song.chart"
   ```

The no-argument command checks every `.chart` in the incoming folder. It continues
past bad files so other reports can still be produced. A failure gives a nonzero
exit status. With no input files it says so rather than pretending an import ran.
Inputs and outputs are ignored by Git to prevent accidental redistribution.
The tool never downloads or opens audio referenced in metadata.

## Reading the result

- **`prepared_not_playable`** means the supported guitar data passed validation
  and was generated. It does **not** mean the song can already replace the demo.
- **`invalid`** means an error prevented generation. The report gives an error
  code, explanation and source line when available. Correct the chart in its
  editor and import again; do not bypass the error or delete difficult notes.
- **Warnings** explain preserved features that gameplay does not support, a
  layout mismatch, an unverified recording or editor/metadata assumptions.
- **Info** entries identify retained editor-only data such as tempo anchors.

Each successful folder contains:

| File | Purpose |
| --- | --- |
| `report.txt` | Readable metadata, difficulty summaries and problems |
| `report.json` | Same structured validation/compatibility results for tools |
| `song.json` | Full normalized song data, exact times, raw metadata/events |
| `song_data.hpp` | Prepared C++17 tables that compile with the GBA compiler; separate from the live game's old Note format |

Rerunning an import replaces only these generated files. A failed re-import
removes its old `song.json`/header so stale data cannot look like a new success.
Do not keep hand-written files under those names in the generated folder, and
run only one import process per output folder at a time. `--output-dir PATH`
selects a different output root, still with one subfolder per input filename.

## What is supported

- UTF-8/BOM `.chart` files with standard sections and `//` comments.
- Song metadata, positive resolution, and **all** BPM changes from SyncTrack.
- Exact cumulative tempo conversion, including notes right at a tempo change.
- Time signatures as metadata. They do not change the quarter-note tick unit.
- Independent EasySingle, MediumSingle, HardSingle and ExpertSingle lead-guitar
  tracks; simultaneous notes retain their original file order.
- Logical frets 0–4, open notes (identifier 7), sustain lengths/end times across
  tempo changes, and signed decimal `.chart` Offset values.
- Strum/HOPO-flip (5) and tap (6) markers retained as modifiers, not extra notes.
- Phrase/text/global events retained; unknown instrument tracks retained as raw
  rows. Their gameplay behavior is not implemented.
- Explicit validation of duplicate/unsorted events, missing tempo/resolution,
  unknown note identifiers, malformed input and timestamp overflow.

## What remains unsupported

MIDI, six-fret guitar, drums/bass gameplay, external `song.ini` overrides, automatic
HOPO/strum rules, open/sustain gameplay, star power, solo events, new difficulty
screens, audio conversion, new song selection and automatic game integration are
not implemented. A neighboring `song.ini` is detected and warned about but not
read/applied. Editor anchors are preserved and compared with the tempo map;
they do not silently override it. Missing initial BPM is an error, even though
some other programs assume a default. Missing meter stays unspecified with a
warning because it is not required to calculate elapsed seconds.

The importer preserves unsupported data rather than secretly dropping flags,
turning opens into fretted notes, shortening sustains, changing difficulty or
squeezing five frets into four. The generated header contains notes, modifiers,
tempo and meter tables; JSON also retains phrases, text, anchors and unknown
sections. Keep the JSON alongside the header for future integrations.

## Future difficulty layouts

| Difficulty | Future left-to-right buttons | Status today |
| --- | --- | --- |
| Easy | D-pad Left, A, B | Data preparation only; no three-lane renderer |
| Medium | D-pad Left, D-pad Right, A, B | Existing controls, but new imported clock/audio adapter still needed |
| Hard | D-pad Left, D-pad Up, D-pad Right, A, B | Data preparation only; no five-lane renderer |
| Expert | Not automatically assigned | Original community difficulty stays Expert |

Chart lanes stay logical fret numbers. Three distinct notes using lanes 0, 2, 4
still require five logical fret slots; they are not silently remapped to 0, 1, 2.
A future three/four-lane chart needs an authorized authored arrangement or an
explicit designer-approved policy. Difficulty names alone do not prove a fit.

D-pad Left+Right is normally impossible on physical hardware. Left+Up/Up+Right
are possible diagonals but may be uncomfortable. Reports identify these chords
for the planned layouts without deleting or modifying the notes. These checks
cover same-tick note onsets, not overlapping held sustains or human ergonomics;
those need validation before future sustain gameplay. Emulator opposing-direction
behavior is not proof of physical playability.

## Why the recording must match

The next target is **Sunshine of Your Love by Cream**. No authorized chart or
new audio was supplied or fabricated in this mission. A Guitar Hero III **cover**
chart may follow a different performance from Cream's original recording.
Same title does not mean matching intro length, tempo, arrangement or recording.
An offset adjustment cannot fix a different performance's changing timing.

For a future authorized import, keep the chart's exact recording/version and
license, obtain the matching recording with appropriate permissions, review any
`Offset` and `song.ini` delay, and measure beginning/middle/end alignment. Our
normalized audio-origin time is **tempo-map time + chart Offset**. A positive
Offset means chart notes occur later relative to audio sample zero (equivalently,
audio begins sooner relative to chart zero). Negative times require a future
pre-roll policy. No audio is shifted by this importer.

Only after recording/rights verification, a tested absolute-time gameplay adapter,
and any required lane renderer exist should the new data/audio be connected to
the game. Until then, use the unchanged demo ROM for play testing. Mission 004
should address that explicit integration/calibration decision, not assume an
import report has already done it.
