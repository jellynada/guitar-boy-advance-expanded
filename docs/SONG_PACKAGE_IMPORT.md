> Mission 005 adds an explicit **silent Easy gameplay adapter** after import.
> The original demo clock and judgment formulas remain unchanged. Inspection
> reports alone still do not make arbitrary packages playable. See
> [GBA_CHART_ADAPTATION.md](GBA_CHART_ADAPTATION.md) for the opt-in runtime,
> three-lane controls, preparation rules and current limits.

# Import a Clone Hero song package — Mission 004

This tool inspects and prepares song data on your computer. **It does not turn a
new song into a playable ROM yet.** The existing demo still plays its original
music/chart with Left, Right, A, B. You do not need a GBA compiler to import.

## Start here

Install Python **3.10 or newer** from https://www.python.org/downloads/ (on Windows,
select the installer option to add Python to PATH). No pip packages are needed.
Unzip the review bundle. Open a terminal in that folder: on Windows, open the
folder in File Explorer, click its address bar, type `cmd`, then Enter. On macOS,
open Terminal, type `cd `, drag the extracted folder into it, then Enter.

Try the original synthetic example, which contains no real song or audio:

```text
python3 tools/import_song.py tests/fixtures/midi
```

Windows can use `py -3` instead of `python3`. Open
`imports/output/packages/midi/report.txt` after the command finishes. A missing
audio warning is expected for this test fixture.

For your own authorized song, put its ZIP in `imports/incoming`, then run:

```text
python3 tools/import_song.py
```

Or select the ZIP directly (quotes keep spaces in filenames together):

```text
python3 tools/import_song.py "path/to/song.zip"
```

An extracted folder, individual `.chart`, `.mid`, or `.midi` is also accepted:

```text
python3 tools/import_song.py "path/to/extracted song"
python3 tools/import_song.py "path/to/song/notes.mid"
```

The no-argument command processes immediate folders/ZIPs/chart files in incoming,
continues after invalid packages, and exits unsuccessfully if any fail. Duplicate
output names are rejected: import those separately with different `--output-dir`
values. Default package output is separate from Mission 003 chart-only output.
Do not run concurrent imports into the same output folder. Imported private
files/output are ignored by Git; this is not a license to redistribute them.

## If the tool asks you to choose

It prints choices and writes an error report instead of guessing. Use a relative
path shown in that report, including any containing folder inside the ZIP:

```text
python3 tools/import_song.py "song.zip" --chart "Song/notes.mid"
python3 tools/import_song.py "song.zip" --audio "song.opus" --audio "guitar.opus" --audio "rhythm.opus"
```

Multiple standard stems (`song`, `guitar`, `rhythm`, bass, keys, vocals, drums,
crowd and supported numbered vocals/drums) are a recognized layout. Competing
formats for the same stem or unknown stem names require explicit `--audio`
selection. This records choices for a future adapter; it does not mix audio.
`preview.*` is a preview, never a replacement for the song. Only files beside the
chosen chart are paired. Other folders remain in the inventory.

INI metadata takes priority over chart display metadata. Original values are
retained. `song.ini delay` is in milliseconds, positive meaning later chart notes.
Chart `Offset` is seconds, also positive meaning later chart notes relative to
audio zero. A single nonzero offset is applied once. When both are nonzero,
choose after checking the source's intended timing:

```text
python3 tools/import_song.py "song.zip" --offset-policy ini
```

`ini` uses only INI delay, `chart` uses only chart Offset, `add` adds both.
The tool deliberately requires this choice rather than assuming every player
uses the same precedence. Reports retain both raw values and effective offset.
Audio bytes are never shifted. Negative times need future pre-roll support.

## Reading the output

Inside `imports/output/packages/<input-name>/`:

| File | Purpose |
| --- | --- |
| `report.txt` | Human-readable title, artist, format, instruments, difficulties, note/chord/sustain counts, tempo/meter, offsets, audio and problems |
| `report.json` | Same structured findings and per-track compatibility details |
| `song.json` | Full normalized timing, notes, metadata, markers and source provenance |

Reports distinguish `imported_and_normalized`, `imported_with_warnings`, and
`invalid_or_unsupported`. Normalized means the recognized notes were converted.
`ready_for_future_adapter` means basic package files were found and no retained
SysEx needs interpretation; it is **only an inspection readiness flag**, not a
complete certification. Warnings still need review, recording/rights need checking,
and no runtime adapter exists. Missing audio/INI or uninterpreted SysEx keeps
that flag false. Every report has `playable_now: false`.

WARNINGS explain preserved unsupported features; ERRORS stop preparation. Failed
reimports remove old `song.json` so it cannot be mistaken for new success. The
package command generates JSON, not a MIDI C++ header: MIDI modifiers and exact
tempos need a future adapter. Keep JSON as the authoritative artifact. The old
`python3 tools/import_chart.py ...` workflow and its chart-only C++ header still
work unchanged. Use separate output folders for the two workflows.

Available normalized instruments are separate from raw source MIDI track names.
Drums, pro/6-fret guitar, vocals and unknown tracks remain raw events with warnings;
they are not converted into five-fret notes. Source inventory includes optional
artwork, but the tool does not open it or certify file contents.

## MIDI interpretation and accuracy

Supported: bounded Standard MIDI Type 1, and Type 0 when its single track is
explicitly named for a supported instrument and includes the tempo. PPQ timing
only. Recognized five-fret names: `PART GUITAR`, legacy `T1 GEMS`, `PART BASS`,
`PART RHYTHM`, `PART GUITAR COOP`, `PART KEYS`. The current game only plays its
original lead-guitar demo. Type 0 is an inspection extension; Clone Hero commonly
expects Type 1. Arbitrary music MIDI is not a Clone Hero chart.

The reader validates chunks, lengths, four-byte VLQs, delta-to-absolute ticks,
channel bytes, running status, end-of-track and note pairing by track/channel/pitch.
Velocity-zero note-ons are note-offs. Ambiguous overlapping same-pitch note-ons,
unmatched offs, unclosed notes and duplicate logical lanes fail explicitly.
Running status resets on meta/SysEx; nonstandard files continuing it are rejected.
An explicit positive tempo at tick zero is required; no missing-tempo 120 BPM guess.
Type 2, SMPTE timing/offsets, conflicting tempos and malformed meter fail.

Frets use Easy60–64, Medium72–76, Hard84–88 and Expert96–100. Difficulties stay
separate. Note-based opens (59/71/83/95) require `[ENHANCED_OPENS]` at tick zero;
otherwise those pitches remain uninterpreted events. Force-HOPO/strum markers
(base+5/+6) are modifiers, not fret notes. Markers104/116 identify tap/star power;
103 is retained as ambiguous solo/legacy-star-power, with no guessed precedence.
Versus, trill, tremolo and big-rock-ending markers are also preserved. Unknown
pitches, text, controller events and SysEx bytes remain available in JSON.

Phase Shift open/tap SysEx is identified and retained with explicit warnings;
its range effects are **not** applied to notes. Inspectors must not treat those
normalized fret lanes as final. Automatic HOPO rules, player sustain cutoff,
chord snapping and INI gameplay overrides are likewise not applied. Original
note release lengths are retained, even a one-tick note. Thus sustain counts
refer to source lengths, not the sustain display a specific player would choose.

Both formats use the same exact rational TempoMap and note span representation.
MIDI stores microseconds per quarter directly; a tempo such as500001 is never
rounded into milli-BPM. Note boundaries use cumulative time at the boundary;
sustains integrate every segment up to their release. Microseconds round once at
export, nearest with half away from zero; duration=rounded end−rounded start.
Tests use independent expected times and logically equivalent chart/MIDI events.
See `MISSION_004_RESULTS.md` for actual results.

## Package safety and limits

ZIPs are inspected in place, never extracted. Reject traversal, absolute/drive/
backslash paths, symlinks/special files, case-colliding/duplicate paths, file/directory
prefix collisions, encryption, unsupported compression, malformed read entries,
and suspicious decompression. Limits:4096 entries,1GiB per entry,2GiB total,
1000:1 compression ratio,32MiB chart/MIDI read,1MiB INI read,250000 MIDI events.
These deliberate limits can reject unusually large legitimate packages.
Only stored/deflated ZIPs are supported. Folder symlinks/special files are rejected.
Do not modify package files concurrently during inspection.

Only chart/MIDI/INI bytes are read. Archive CRC/content checks therefore cover
read entries, not unopened audio/art files. OGG/MP3/WAV/OPUS detection is by file
extension; malformed audio is not discovered in this mission. No imported
scripts, executables or commands run. Inspection does not establish licensing.

## Test Sunshine of Your Love privately

The named package was **not present** in this cloud workspace. No actual notes,
audio, difficulty counts or timing from it have been analyzed here. Place your
copy next to the extracted tools and run:

```text
python3 tools/import_song.py "Cream (WaveGroup) - Sunshine of Your Love (Neversoft).zip"
```

Open `imports/output/packages/Cream (WaveGroup) - Sunshine of Your Love (Neversoft)/report.txt`.
It should discover the reported MIDI/INI/OPUS layout if those files are present.
This is an expectation to verify, not a result. Share the report if you want help;
keep the chart/audio private. Do not assume a WaveGroup cover aligns with Cream's
original recording just because the title matches.

## Future lane mapping and audio

Native lanes are never collapsed, and Expert stays Expert. Planned Easy is
Left/A/B, Medium Left/Right/A/B, Hard Left/Up/Right/A/B. Reports show distinct lanes
and the maximum logical slot required (lanes0,2,4 still need five slots). They flag
same-tick opposing D-pad/diagonal chords and overlapping native sustains. Expert
has no approved mapping. Human playability remains unverified.

Future adapter interface proposal (design only):

```json
{"mapping_version":1,"source_instrument":"five_fret_lead_guitar",
 "source_difficulty":"Medium","target_layout":"Medium",
 "lane_to_button":{"0":"Left","1":"Right","2":"A","3":"B"},
 "unmapped_lane_policy":"reject","open_note_policy":"reject",
 "modifier_policy":"require_explicit_policy","sustain_policy":"require_explicit_policy"}
```

Validate every source lane, collision, simultaneous hold and approved target
button before compiling. Mapping lives outside source notes; no automatic
five-to-three/four reduction or Expert relabeling. The existing renderer is untouched.

Stem names are preparation for a future audio mixer. An isolated guitar stem
could eventually react to judgment events while backing stems continue. Discovery
does not prove a stem is isolated or playable on GBA. Future work must establish
codec/size/CPU budget, decode or convert authorized audio, define a sample-aligned
audio clock and validate beginning/middle/end synchronization before reactive
mixing. None of compression, muting, mixing, menus or new fretboards is implemented.
