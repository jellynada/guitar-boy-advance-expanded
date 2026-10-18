# Guitar Boy Advance Expanded — Mission 001

A four-lane Game Boy Advance rhythm-game prototype based on
[startfliing's Guitar Boy Advance](https://github.com/startfliing/guitar-boy-advance).
Mission 001 makes the existing game build reliably and prevents reading beyond the
song data. It preserves the original highway, artwork, module music, buttons,
and timing calculations. It does not add gameplay features.

## Play the ROM (no programming needed)

1. Download **mGBA** for your computer from https://mgba.io/downloads.html.
   Windows: extract the downloaded ZIP and open mGBA. macOS: open the disk image
   and drag mGBA into Applications. Linux: install mGBA using your distribution's
   software manager (Ubuntu/Debian package: `mgba-qt`).
2. Obtain `guitar-boy-advance-expanded.gba` from this cloud workspace's file
   browser after building; select the file and use Download. The full location
   is `/workspace/guitar-boy-advance-expanded/guitar-boy-advance-expanded.gba`.
   The ROM is a generated file, so it is not included in a Git checkout.
3. In mGBA, choose **File → Load ROM** and select that `.gba` file. A separately
   downloaded Nintendo BIOS is not required for this workflow.
4. Open mGBA's keyboard/controller settings and assign convenient keys to the
   four GBA buttons below. Keyboard defaults can vary; these are GBA button names,
   not the letters you must press on your computer.

| Lane, from left to right | GBA button |
| --- | --- |
| Green | L shoulder |
| Red | B |
| Yellow | A |
| Blue | R shoulder |

Press the matching button as a note reaches the fret circles. There is no
separate strum button. Simultaneous notes expect the matching buttons together.
The song starts automatically; there is no menu, pause, song selection, or results
screen. Reset/reload the ROM to start over. Music loops, but the chart does not
restart; that existing limitation is unchanged. `CONTROLS_ENABLED = false` turns
off the developer's camera controls, **not** the rhythm-game buttons.

The automated mGBA test checks rendering, audio samples, button input and reaching
the end of the chart. Please also play a full song: check the sound, visual
alignment and button response yourself. Automated testing cannot judge play feel.

## Build it using Docker (recommended for a repeatable build)

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
folder. Internet access is needed to download the image initially. The script
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

Make automatically compiles `bin/chart_reader.cpp` for your computer. The old
Windows `.exe` files stay in the repository but are not used for this song.
Do not look online for a replacement `note.h`: the converter creates it under
`build/`, together with `careless.h` and `careless.s`. Graphics and audio headers,
assembly, soundbank, object files, `.elf` and `.gba` are generated too.

If Make says `DEVKITARM` is missing, use the Docker commands or the export lines
above. If it reports unsupported `&:` rules, your Make is older than 4.3. If
`g++` is missing, install a desktop C++ compiler or use Docker. A CSV converter
exists only as a Windows binary; there are no CSV inputs in this game and it is
not required. Do not add CSV inputs as part of Mission 001.

## Developer checks and project status

Run `bash tests/check.sh` with desktop GCC and Python 3 installed. This checks
the real note manager under memory/undefined-behavior sanitizers, the 699 chart
records, unchanged timing conversion, and rejection of missing/zero resolution.
The text renderer is stubbed for this host test; it is exercised by the ROM.

See [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md) for architecture, known
limitations, emulator test instructions, and the suggested next work.

## Credits and asset rights

Original game: startfliing. The Mode 7 files retain J Vijn's attribution and the
existing Tonc-based code. The included track is `careless_whisper.mod`; its
embedded credits mention Basil Fawlty / Scope-1990. This checkout does not supply
a project license or complete artwork/music permissions. Keeping the existing
assets does not establish permission to distribute them or the compiled ROM.
Confirm permissions before public distribution; no substitute assets or new
license claims are introduced here.
