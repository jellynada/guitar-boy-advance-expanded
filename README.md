# Guitar Boy Advance Expanded — Mission 006

A Game Boy Advance rhythm prototype based on [startfliing's original project](https://github.com/startfliing/guitar-boy-advance).
Imported Easy Test now **plays prepared audio**, with notes timed from the GBA
sample timer. The public ROM has an original 25-note triangle-tone exercise.
The owner's matching Cream/WaveGroup cover was decoded, mixed and tested privately
with all 395 Easy notes. Private charts, recordings and their ROM are excluded
from the public bundle. No sustain mechanics, reactive mixing or scoring added.

## Start here

[Download the Mission 006 review bundle](https://github.com/jellynada/guitar-boy-advance-expanded/raw/refs/heads/mission-006-download/downloads/mission006-review.zip),
unzip it and load `guitar-boy-advance-mission-006.gba` in mGBA. Use GBA Up/Down,
then A or Start, to choose **Original Demo** or **Imported Easy Test**.
Start+Select returns to the selector for a clean restart.

- Original Demo: **Left / Right / A / B**, existing music and 699 notes.
- Imported Easy Test: **Left / A / B**, matching synthetic audio and 25 notes.

Map those GBA buttons to convenient computer keys in mGBA settings. The public
synthetic test has a two-second pre-roll. Read `READ_ME_FIRST.txt` in the bundle.

For **Windows 11**, use [GBA_AUDIO_PIPELINE.md](docs/GBA_AUDIO_PIPELINE.md).
After the documented Ubuntu/WSL, Docker and FFmpeg installation, put your private
Cream ZIP in imports/incoming and run these two commands in Ubuntu:

```bash
python3 tools/prepare_song.py "imports/incoming/Cream (WaveGroup) - Sunshine of Your Love (Neversoft).zip" --stem guitar --stem rhythm --stem song
bash scripts/build-docker.sh "IMPORTED_HEADER=imports/output/song-runtime/imported_chart.hpp" "AUDIO_DIR=imports/output/song-runtime/audio"
```

Open the resulting `guitar-boy-advance-expanded.gba` in mGBA and select Imported
Easy Test. No source editing or Git commands are needed with the full-source
bundle. The explicit stems include guitar, rhythm and song; preview is excluded.

Existing chart/package inspectors and `tools/prepare_easy.py` still work. A private
chart built without prepared audio uses a labeled **SILENT FALLBACK**. Supplying
missing/corrupt AUDIO_DIR data fails; it cannot substitute the original soundtrack.
Python3.10+ and FFmpeg/ffprobe are host-conversion dependencies. Public synthetic
builds need only Python and the existing pinned GBA toolchain/container.
See [results](docs/MISSION_006_RESULTS.md) for measured limits; perceived sync,
physical hardware and sound quality still need a person to test.

## Play the ROM (no programming needed)

1. Download **mGBA** for your computer from https://mgba.io/downloads.html.
   Windows: extract the downloaded ZIP and open mGBA. macOS: open the disk image
   and drag mGBA into Applications. Linux: install mGBA using your distribution's
   software manager (Ubuntu/Debian package: `mgba-qt`).
2. Download the [Mission 006 ZIP bundle](https://github.com/jellynada/guitar-boy-advance-expanded/raw/refs/heads/mission-006-download/downloads/mission006-review.zip)
   and unzip it. If clicking does not download, [open the file page](https://github.com/jellynada/guitar-boy-advance-expanded/blob/mission-006-download/downloads/mission006-review.zip)
   and click the **Download raw file** arrow. The game inside is named
   `guitar-boy-advance-mission-006.gba`, and includes the selector and synthetic three-lane test.
3. In mGBA, choose **File → Load ROM** and select that `.gba` file. A separately
   downloaded Nintendo BIOS is not required for this workflow.
4. Open mGBA's keyboard/controller settings and assign convenient keys to the
   four GBA buttons below. Keyboard defaults can vary; these are GBA button names,
   not the letters you must press on your computer.

| Lane, from left to right | GBA button |
| --- | --- |
| Green (Original / Easy) | D-pad Left |
| Red (Original) | D-pad Right |
| Yellow (Original) / Red (Easy) | A |
| Blue (Original) / Yellow (Easy) | B |

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
3. Press an incorrect active lane button: WRONG should flash. The valid upcoming note should
   still be playable. A correct button plus an extra wrong button can show both
   a hit and WRONG; the valid hit is kept.
4. Play through the song, or let it finish: H + M should end at **699** in Original Demo, **25** in the public Easy fixture, or **395** in the privately prepared Cream Easy test.

Chords are handled note by note; a partial chord can earn hits for pressed members
while the others miss. The existing demo contains no chords. A physical D-pad
normally cannot press Left and Right together, so future charts must consider
that limitation.

Choose a mode at the initial selector. Start+Select returns there to replay.
There is no pause or results screen. Original music loops but its chart does not reset.
Automated mGBA runs verify the game and counters; please also judge the sound,
alignment and button response yourself. We have not manually played or listened
to this build. Your working Mission 001 and Mission 002 downloads remain unchanged.

## Build it using Docker (recommended for a repeatable build)

These build commands require the complete Mission 006 source, included in
the review bundle or available on `mission-006-audio-sync`. The review bundle includes the playable ROM and
complete source, original build assets and tools. Import and build commands
work from its extracted project folder.

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
folder (the download bundle gives its copy the clearer Mission 006 filename). Internet access is needed to download the image initially. The script
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
Native builds also need Python 3.10+. The Docker recipe is the tested version reference; other versions are unverified.
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
run `bash tests/run_audio_emulator.sh perfect 1800 /tmp/synthetic` for the public audio test;
run `bash tests/run_emulator.sh perfect` for the original demo, then the same command with `miss` or
`mixed`. Each runs about ten minutes of emulated time. These are optional tools
for developers; you can simply load the downloaded ROM in mGBA.

See [project status](docs/PROJECT_STATUS.md), [import instructions](docs/CHART_IMPORT_GUIDE.md),
[judgment rules](docs/NOTE_JUDGMENT.md), [Mission 006 results](docs/MISSION_006_RESULTS.md)
and [historical Mission 002 results](docs/MISSION_002_RESULTS.md).
Source branch: `mission-006-audio-sync`; no automatic merge into main.
[Review Mission 006 changes](https://github.com/jellynada/guitar-boy-advance-expanded/compare/mission-005-first-playable-import...mission-006-audio-sync).

## Credits and asset rights

Original game: startfliing. The Mode 7 files retain J Vijn's attribution and the
existing Tonc-based code. The included track is `careless_whisper.mod`; its
embedded credits mention Basil Fawlty / Scope-1990. This checkout does not supply
a project license or complete artwork/music permissions. Keeping the existing
assets does not establish permission to distribute them or the compiled ROM.
Confirm permissions before public distribution; no substitute assets or new
license claims are introduced here.
