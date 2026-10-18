# Guitar Boy Advance Expanded — Mission 003

A four-lane Game Boy Advance rhythm-game prototype based on
[startfliing's Guitar Boy Advance](https://github.com/startfliing/guitar-boy-advance).
Mission 003 adds a computer-side community chart importer and validator. It
prepares tempo-aware song data without changing the working Mission 002 game.
The existing ROM, note judgments, music, graphics and **Left / Right / A / B**
controls are unchanged. No new song, audio, lane renderer or gameplay is added.

## Inspect a chart — no C++ editing needed

Install Python 3.10+ if necessary. To try the included original synthetic example:

```text
python3 tools/import_chart.py tests/fixtures/charts/tempo_changes.chart
```

Open `imports/output/tempo_changes/report.txt`. To inspect your own authorized
chart, place its `.chart` in `imports/incoming/` and run:

```text
python3 tools/import_chart.py
```

On Windows, `py -3` can replace `python3`. The download bundle includes these tools
and fixtures, so you do not need to learn Git to try them. No audio is downloaded
or opened. Successful import means **prepared, not yet playable**: the current
game still uses its original chart/clock until a separately tested adapter exists.

Read the [beginner import guide](docs/CHART_IMPORT_GUIDE.md),
[song-data format](docs/SONG_DATA_ARCHITECTURE.md) and
[Mission 003 results](docs/MISSION_003_RESULTS.md). No authorized Sunshine of Your
Love chart was provided; no Cream recording or Guitar Hero III assets were imported.

## Play the ROM (no programming needed)

1. Download **mGBA** for your computer from https://mgba.io/downloads.html.
   Windows: extract the downloaded ZIP and open mGBA. macOS: open the disk image
   and drag mGBA into Applications. Linux: install mGBA using your distribution's
   software manager (Ubuntu/Debian package: `mgba-qt`).
2. Download the [Mission 003 ZIP bundle](https://github.com/jellynada/guitar-boy-advance-expanded/raw/refs/heads/mission-003-download/downloads/mission003-review.zip)
   and unzip it. If clicking does not download, [open the file page](https://github.com/jellynada/guitar-boy-advance-expanded/blob/mission-003-download/downloads/mission003-review.zip)
   and click the **Download raw file** arrow. The game inside is named
   `guitar-boy-advance-mission-003.gba`, but its game bytes match Mission 002 exactly.
3. In mGBA, choose **File → Load ROM** and select that `.gba` file. A separately
   downloaded Nintendo BIOS is not required for this workflow.
4. Open mGBA's keyboard/controller settings and assign convenient keys to the
   four GBA buttons below. Keyboard defaults can vary; these are GBA button names,
   not the letters you must press on your computer.

| Lane, from left to right | GBA button |
| --- | --- |
| Green | D-pad Left |
| Red | D-pad Right |
| Yellow | A |
| Blue | B |

A suggested computer-keyboard mapping is **D, F, J, K**: assign GBA Left to D,
Right to F, A to J, and B to K in mGBA's controls settings. These are suggestions,
not required keyboard defaults. The D-pad controls play notes; the camera stays fixed.

Press the matching button as a note reaches the fret circles. There is no strum
button. The screen shows the latest **PERFECT**, **GOOD**, or **MISS**. **H:** is
the number of notes hit; **M:** is the number missed. **WRONG** briefly appears
for a wrong press. A held button cannot hit later notes: release and press again.
Perfect means within 25 ms of the note; Good permits up to 50 ms early/85 ms late.
You do not need to understand those numbers to play.

To check the new behavior yourself:

1. Let several notes pass without pressing anything: M should increase.
2. Press the correct lane near its circle: H should increase once and show
   PERFECT or GOOD. Hold that button: H should not keep increasing.
3. Press an unrelated button: WRONG should flash. The valid upcoming note should
   still be playable. A correct button plus an extra wrong button can show both
   a hit and WRONG; the valid hit is kept.
4. Play through the song, or let it finish: H + M should end at **699**.

Chords are handled note by note; a partial chord can earn hits for pressed members
while the others miss. The existing demo contains no chords. A physical D-pad
normally cannot press Left and Right together, so future charts must consider
that limitation.

The song starts automatically. There is no menu, pause or results screen.
Reset/reload the ROM to replay. Music loops but the chart does not reset.
Automated mGBA runs verify the game and counters; please also judge the sound,
alignment and button response yourself. We have not manually played or listened
to this build. Your working Mission 001 and Mission 002 downloads remain unchanged.

## Build it using Docker (recommended for a repeatable build)

These build commands require the complete source repository on
`mission-003-chart-importer`. The review bundle includes the playable ROM and
standalone import tools/examples, not every original game build asset. Import
inspection commands above work directly from the extracted bundle.

A build turns the source code and assets into the `.gba` cartridge file.
Install Docker Desktop from https://www.docker.com/products/docker-desktop/
(or Docker Engine on Linux), start it, and open a Bash terminal in this project
folder. On Windows use a WSL2 Linux terminal with Docker integration enabled.
Keep the checkout in the Linux filesystem and use Linux containers.

Run each line separately:

```bash
bash scripts/build-docker.sh clean
bash scripts/build-docker.sh
```

The second command creates `guitar-boy-advance-expanded.gba` in the project
folder (the download bundle gives its copy the clearer Mission 003 filename). Internet access is needed to download the image initially. The script
pins the official devkitPro image by its content digest, rather than using a
moving `latest` tag. It includes devkitARM GCC 16.1.0, libtonc, libgba/Maxmod,
`grit`, `mmutil`, `gbafix`, GNU Make 4.3 and desktop GCC 12.2.0. The game uses
C++17. The first command discards only generated build outputs; it does not
remove source or assets. Do not run `clean` and the build at the same time.

## Build inside the prepared cloud environment

Open a terminal and paste these commands:

```bash
cd /workspace/guitar-boy-advance-expanded
export DEVKITPRO=/workspace/.cloud-setup/gba/devkitpro
export DEVKITARM="$DEVKITPRO/devkitARM"
export PATH="$DEVKITARM/bin:$DEVKITPRO/tools/bin:$PATH"
make clean
make -j2
```

For another native Linux installation, install the official devkitPro `gba-dev`
toolchain (https://devkitpro.org/wiki/Getting_Started), desktop `g++` with C++17,
and GNU Make **4.3 or newer**, then set `DEVKITPRO`/`DEVKITARM` to its locations.
The Docker recipe is the tested version reference; other versions are unverified.
`HOSTCXX=clang++` or another host compiler can be passed to Make if necessary.

Make automatically compiles `bin/chart_reader.cpp` for your computer and caches
a separate helper for each compiler target/version, so native and Docker builds
do not accidentally reuse incompatible desktop programs. The old
Windows `.exe` files stay in the repository but are not used for this song.
Do not look online for a replacement `note.h`: the converter creates it under
`build/`, together with `careless.h` and `careless.s`. Graphics and audio headers,
assembly, soundbank, object files, `.elf` and `.gba` are generated too.

If Make says `DEVKITARM` is missing, use the Docker commands or the export lines
above. If it reports unsupported `&:` rules, your Make is older than 4.3. If
`g++` is missing, install a desktop C++ compiler or use Docker. A CSV converter
exists only as a Windows binary; there are no CSV inputs in this game and it is
not required. CSV inputs are outside this mission.

## Developer checks and project status

Run `bash tests/check.sh` with desktop GCC and Python 3. It tests judgment under
memory/undefined-behavior sanitizers, all timing boundaries and input rules, and
two runs of the unchanged 699-note chart. Leak checking is enabled as well.
It also runs the new importer fixtures, exact timing checks, report/CLI checks and
generated-header compilation checks (GBA check is explicitly skipped if devkitARM
is absent).

With mGBA development headers/library installed, `DEVKITARM` set and a built ROM,
run `bash tests/run_emulator.sh perfect`, then the same command with `miss` or
`mixed`. Each runs about ten minutes of emulated time. These are optional tools
for developers; you can simply load the downloaded ROM in mGBA.

See [project status](docs/PROJECT_STATUS.md), [import instructions](docs/CHART_IMPORT_GUIDE.md),
[judgment rules](docs/NOTE_JUDGMENT.md), [Mission 003 results](docs/MISSION_003_RESULTS.md)
and [historical Mission 002 results](docs/MISSION_002_RESULTS.md).
Source branch: `mission-003-chart-importer`; no automatic merge into main.
[Review Mission 003 changes](https://github.com/jellynada/guitar-boy-advance-expanded/compare/mission-002-note-judgment...mission-003-chart-importer).

## Credits and asset rights

Original game: startfliing. The Mode 7 files retain J Vijn's attribution and the
existing Tonc-based code. The included track is `careless_whisper.mod`; its
embedded credits mention Basil Fawlty / Scope-1990. This checkout does not supply
a project license or complete artwork/music permissions. Keeping the existing
assets does not establish permission to distribute them or the compiled ROM.
Confirm permissions before public distribution; no substitute assets or new
license claims are introduced here.
