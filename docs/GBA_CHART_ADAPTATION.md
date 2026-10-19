> Mission 006 update: imported audio is now supported. For the current Windows 11
> **one preparation command + one build command with matching sound**, follow
> [GBA_AUDIO_PIPELINE.md](GBA_AUDIO_PIPELINE.md). The chart-only commands below
> remain available as a labeled silent fallback. The private Cream chart/audio
> have both been played end to end in the emulator; neither is published.

# Mission 005: play an imported Easy chart

**Imported Easy Test is onset-only gameplay.** Mission006 adds prepared PCM sound;
chart-only builds use SILENT FALLBACK. No held-note scoring, sustain tails or reactive audio.
The current public ROM contains an original25-note synthetic chart and matching audio, clearly labeled.
The owner's actual395-note Cream/WaveGroup Easy chart was built/tested privately;
its source, normalized notes and chart-containing ROM are not published.

## Try the public ROM first

Download/unzip the Mission 005 review bundle. Install mGBA from
https://mgba.io/downloads.html. In mGBA choose File → Load ROM and open
`guitar-boy-advance-mission-006.gba`.

The selector has **Original Demo** and **Imported Easy Test**. Use GBA Up/Down to
choose, then A or Start. Audio-enabled builds display SYNTH/AUDIO or LOCAL/AUDIO. The chart-only
commands on this page select the explicitly labeled SILENT FALLBACK. Map these GBA controls in
mGBA settings; computer keyboard defaults vary:

| Mode | Buttons, left to right | Suggested computer keys |
| --- | --- | --- |
| Original Demo | Left, Right, A, B | D, F, J, K |
| Imported Easy Test | Left, A, B | D, J, K |

Press at the fret circles, release and press again for later notes. Right is
ignored in Easy. There is no strum button or hold requirement. Genuine sustain
onsets are played like normal notes in this test. Hold GBA Start+Select together
to return to the selector. Choosing either mode starts a fresh clock, counts,
note states, held-input history, camera, floor, fret circles and audio state.
Original music starts only in Original Demo. Imported mode stays silent.

## Windows 11: chart-only silent fallback, without editing code

The review bundle contains the complete tracked source, tools and original build
assets, so no Git commands are needed. New third-party chart/audio is excluded.
Use the full source folder for these steps, not a folder containing only the ROM.

### One-time installation

1. Install WSL with Ubuntu using Microsoft's instructions:
   https://learn.microsoft.com/windows/wsl/install . The usual command in an
   Administrator PowerShell is `wsl --install`; restart if prompted, then finish
   Ubuntu's first-run user setup. Ask for help with your computer's install errors
   rather than pasting unrelated commands from websites.
2. Install Docker Desktop: https://www.docker.com/products/docker-desktop/ .
   Enable its WSL2 backend and Ubuntu integration in Settings → Resources → WSL
   Integration. Start Docker Desktop and leave it running.
3. Open **Ubuntu** from Start. Install the host Python/tools once:

```bash
sudo apt update
sudo apt install python3
```

No pip packages are required. The pinned Docker image supplies the GBA compiler,
Tonc, Maxmod, graphics/audio tools and its own Python3. Do not install an engine
such as Butano or manually run the old Windows converter EXE.

### Prepare and build

In Ubuntu open the extracted source folder. If Windows extracted it to
`C:\Users\YOURNAME\Downloads\mission005-review`, use:

```bash
cd "/mnt/c/Users/YOURNAME/Downloads/mission005-review"
```

Replace YOURNAME and folder name with your real paths. For faster builds you may
copy the extracted folder into your Ubuntu home, but this is optional. Place your
private song ZIP in `imports/incoming` inside that source folder, then run:

```bash
python3 tools/prepare_easy.py "imports/incoming/Cream (WaveGroup) - Sunshine of Your Love (Neversoft).zip"
```

Read `imports/output/easy-runtime/adaptation_report.txt` and the readable source
report under `imports/output/easy-runtime/source/<package-name>/report.txt`.
The preparation command explicitly selects Easy lead guitar. No Python/C++ edits.
If the package has multiple charts/audio choices or competing offsets, follow
the report and repeat with `--chart`, repeated `--audio` or `--offset-policy` as
explained in SONG_PACKAGE_IMPORT.md. It will not guess, drop notes or remap frets.

Then build:

```bash
bash scripts/build-docker.sh "IMPORTED_HEADER=imports/output/easy-runtime/imported_chart.hpp"
```

The first run downloads the pinned official toolchain image. When it succeeds,
open `guitar-boy-advance-expanded.gba` from that source folder in mGBA. Choose
Imported Easy Test. Your real chart should now display395 notes with Left/A/B,
**in silence**. The first note is4.322 seconds after chart audio zero, plus the
2-second test pre-roll, so wait about6.322 seconds from choosing the mode.
The Docker helper always names this output `guitar-boy-advance-expanded.gba`,
even when the extracted folder has a different name. Native Make uses its folder
basename instead.

For an existing native toolchain, run
`make -j2 IMPORTED_HEADER=imports/output/easy-runtime/imported_chart.hpp` with
DEVKITPRO/DEVKITARM configured. Host Python3 is now a build prerequisite.

To build the public synthetic fixture again, omit IMPORTED_HEADER:

```bash
bash scripts/build-docker.sh
```

The build always checks/regenerates its selected header, including switching
back from a private chart; it cannot silently reuse an earlier selection.
Original Demo remains available in both builds. Do not publish your resulting
Cream-chart ROM or generated note files without appropriate rights. Sharing an
input ZIP with this workspace did not establish redistribution rights.

## What adaptation does

`normalized song.json → explicit Easy lead-guitar selection → validation → adapted.json + imported_chart.hpp + adaptation_report.txt`

`tools/prepare_easy.py` combines package inspection and adaptation into one command.
For already normalized data, the lower-level command is:

```text
python3 tools/adapt_chart.py "path/to/song.json" --difficulty Easy --instrument five_fret_lead_guitar --output-dir imports/output/easy-runtime
```

Source JSON and adapted output stay separate. Original timing, native lanes,
order and durations are preserved. Source logical0/1/2 map identically to
Left/A/B. A chart using0/2/4 is rejected; five-fret data is never squeezed into
three lanes, and Expert is never relabeled. Non-lead or non-Easy selection fails.
Open notes/unapplied SysEx lane changes are rejected, not silently treated as frets.
Modifiers/phrases remain in source; the explicit test rule is a fresh press for
every fret onset, without HOPO/strum/tap/phrase gameplay. Reports warn about this.

### Release length versus sustain

The test classification threshold is **ceil(PPQ/3) source ticks**, or one third of
a quarter note. A positive release at or above that threshold is classified as a
genuine sustain. Shorter releases are ordinary onset notes. This is an explicit
Mission 005 test policy, not a claim that every Clone Hero player applies it.

The supplied package declares `sustain_cutoff_threshold=0`. That is preserved and
reported, but the test deliberately uses160 ticks at PPQ480 for classification.
317 Easy releases are shorter;78 are genuine. All395native start/end/duration
records remain in adapted JSON. Genuine lengths also appear in a generated header
array for a later adapter (the compiler may omit an unused array from the ROM).
No tail/hold/release judgment is implemented for either category.

Validation checks integer units/ranges, tick and timestamp ordering, end identity,
native lane bounds, duplicate inputs, source release overflow, sustain overlaps,
and a complete visible-window budget. Same-lane sustained overlaps are warned
about and retained for onset-only play. Easy has only one D-pad direction, so it
cannot create opposing/diagonal D-pad chords. Simultaneous Left/A/B is allowed.
Charts with more than32onsets in any1.2 second window are rejected, never truncated.
Limit8192 notes,2 hours of source time; final late window and tail remain available.
The build/linker also enforces the hardware memory limit. No per-frame allocation.

## Timing contract

Normalized canonical integer microseconds already include the selected chart/INI
offset and all tempo changes. Never multiply these notes by the initial BPM again.
Runtime tick = nearest integer `(start_us + 2,000,000) × 16,777,216 / 1,000,000`.
The existing16-byte Note ABI is unchanged; its duration field is0 because held
judgment is disabled. Future sustain data is separate, with no unit confusion.

Imported gameplay ticks are **GBA CPU cycles**, not the original demo's empirical
chart units. The existing NoteJudgment receives ticksPerFrame=280896, so its
unchanged25 ms Perfect /50 ms early /85 ms late windows become actual clock cycles.
A single VBlank counter is snapped in the main loop; `now = frames × 280896`.
A mode reset starts a new epoch. Monotonic clamping rejects stale backward reads
and caps the imported clock beyond its2-hour chart budget, with a1-second tail.

Hardware frame duration is `280896 /16777216 =16.7427063 ms`, about59.7275Hz.
There is no per-frame millisecond rounding or repeated rounding of tempo segments.
Microsecond→cycle rounding is at most0.029803 microseconds; canonical JSON rounding
was at most0.5 microseconds, so combined timestamp quantization is at most about
0.000530milliseconds. Polling adds up to one frame under uninterrupted normal
processing, independently of song length; stalls can add more. This is not a
human latency calibration or a promise about audible synchronization.

Actual measurements: synthetic reference-frame tests max11.405945 ms;
automated emulator hit scheduling max16.700745 ms for the synthetic25 notes and
16.694248 ms for the real395 notes. These are simulation/input sampling results,
not audio alignment measurements. Tests exercise beginning/middle/end references,
first/final notes, boundary times, one-hour songs, resets and large frame jumps.

## Perspective rendering units

Original Demo's projection, camera speed and note formulas are unchanged.
Imported mode reuses the same Mode7 projection and original art/palette. Its floor
is a derived three-stripe version of the original64 pixel-wide texture, restored
unchanged when Original Demo is selected. Fret centers are screen x48/120/192.

Imported sprites use bounded relative distance, avoiding overflowing world
coordinates late in long songs. World x is0xE380/0xFC00/0x11480. World z is:

```text
camera_z -21000 - trunc(delta_cycles ×83330×16 /(280896×871))
```

Here83330/871 reproduces the existing demo's visual travel rate as a fixed test
speed, **not the imported song's tempo**. At a note's timestamp, delta=0 and its
sprite reaches the original contact depth. One second ahead and200 ms behind
are maintained by two monotonic cursors, with at most32projected notes. The floor
camera wraps by a complete texture; sprites are positioned relative to it so the
wrap cannot jump note positions. Sorting/OAM projection and hit artwork are reused.

## Audio authority comes later

The two-second pre-roll places future audio sample zero at runtime2 seconds.
No audio begins there today. A later audio engine must supply an authoritative
sample-position clock plus known output-buffer latency; choose how VBlank
render/input snapshots relate to that clock and how stalls, pauses and pre-roll
behave. Validate chart/recording alignment at the beginning, middle and end using
the actual WaveGroup cover, not an assumed Cream studio recording. OPUS decoding,
resampling/compression, memory/CPU budgeting and mixing are outside this mission.

## Testing still needed by a person

Play both modes with your configured keyboard/controller. Check note contact,
readability, return/restart behavior and the original demo's sound by ear. Test
on physical hardware before claiming ergonomics or latency. Imported silence is
intentional. There is no scoring system, sustain gameplay, imported Medium/Hard,
new song library, pause framework, reactive audio or full song menu.
