# Guitar Boy Advance Expanded — Mission 009

A Game Boy Advance rhythm prototype based on
[startfliing's original project](https://github.com/startfliing/guitar-boy-advance).
Imported Easy Test now has playable sustains and hold bonuses, built on the
owner-tested Mission 008 HUD/results hotfix. No automatic merge into main.

## Download and play

[**Download the public Mission 009 review ZIP**](https://raw.githubusercontent.com/jellynada/guitar-boy-advance-expanded/refs/heads/mission-009-download/downloads/mission009-review.zip).

1. Download and **Extract All** on Windows.
2. In [mGBA](https://mgba.io/downloads.html), choose **File > Load ROM**.
3. Open **Guitar-Boy-Advance-Mission-009-Synthetic.gba**.
4. Confirm **M009 HOLDS** and choose **Imported Easy Test** using Up/Down and A/Start.

This public ROM contains original synthetic music and 25 note heads, including
six genuine holds. It includes regular taps, simultaneous A+B holds, and new
notes during holds. **It is not the Cream song.**

These are GBA button names; check mGBA's keyboard settings for your PC mappings:

- Imported Easy, left to right: **Left / A / B**.
- Original Demo: **Left / Right / A / B**, original music and 699 notes.
- Results: **A or Start** replays; **B or Select** returns to mode selection.
- **Start+Select** returns to selection during play.

Hit a long note's head, then keep its button held. SCORE, COMBO and MULT remain
visible. Each complete 250ms held earns one bonus point times the multiplier
captured at the head. Releasing early keeps previous points, combo and guitar
sound. Missed heads and wrong new presses retain their normal combo reset and
guitar muting. Holding one button does not prevent pressing another.

## Playing your Cream song

The full supplied Cream/WaveGroup recording and matching 395-head Easy chart
were built and tested locally with **78 genuine sustains**. This mission restricts
public upload of the new Cream ROM without redistribution confirmation. No private
artifact transfer is available here; the supported delivery is a verified local
build using your existing song ZIP.

Follow the [Windows 11 setup and two-command build guide](docs/SUSTAIN_GAMEPLAY.md#windows-11-build-your-cream-rom-locally).
After one-time Ubuntu/WSL, Docker Desktop and FFmpeg setup, copy your song archive
into the source folder as `Cream.zip`, then run these in Ubuntu from that folder:

```bash
python3 tools/prepare_song.py Cream.zip --reactive --guitar-stem guitar --backing-stem rhythm --backing-stem song --output-dir imports/output/mission009
bash scripts/build-docker.sh "IMPORTED_HEADER=imports/output/mission009/imported_chart.hpp" "AUDIO_DIR=imports/output/mission009/audio"
```

Only continue when each command succeeds. Open the resulting
**guitar-boy-advance-expanded.gba** in the source folder. Select Imported Easy
Test and check that the lower menu line says **LOCAL / AUDIO**. The public
fixture says **SYNTH / AUDIO**. Load the new ROM directly, without restoring an
old save state. No programming or source edits are needed.

## Developer build and checks

The project uses C++, devkitARM, Tonc, Maxmod, Grit and the original chart converter.
The Docker script pins the official devkitARM image by digest. For a public
synthetic build, run `bash scripts/build-docker.sh` from the source folder.
Native builds need devkitPRO with those tools/libraries, GNU Make 4.3+, Python 3,
and a desktop C++ compiler. Set DEVKITPRO/DEVKITARM and add their bin directories
to PATH, then run `make -j2`. FFmpeg is needed for private song preparation.

Make compiles the supplied chart reader for the host platform; the old Windows
converter executables remain but are not used. `note.h` and chart/graphics/audio
headers, assembly, soundbank, ELF and ROM are generated under `build/`/the root.
The local `Cream.zip`, imported song outputs and generated ROMs are Git-ignored.

`bash tests/check.sh` runs 98 Python tests and C++ memory/undefined-behavior
sanitizer checks. With mGBA development headers/library and DEVKITARM available:

```bash
bash tests/run_audio_emulator.sh sustain-perfect 1800 /tmp/sustain-perfect
bash tests/run_audio_emulator.sh sustain-release 1800 /tmp/sustain-release
bash tests/run_emulator.sh perfect
```

The audio runner checks actual composed HUD/results pixels, tail pixels, scoring,
replay and menu navigation. Real-song runs need 16,400 frames and the matching
private build; the short 1,800-frame run is for the public synthetic fixture.
NumPy is an optional developer dependency for waveform analysis, not building.

Read [sustain design and edge policies](docs/SUSTAIN_GAMEPLAY.md),
[Mission 009 validation](docs/MISSION_009_RESULTS.md),
[project status](docs/PROJECT_STATUS.md), and
[chart import instructions](docs/CHART_IMPORT_GUIDE.md).
[Review Mission 009 source changes](https://github.com/jellynada/guitar-boy-advance-expanded/compare/mission-008-hotfix-hud-completion...mission-009-sustain-gameplay).

## Credits and asset rights

Original game: startfliing. The Mode 7 files retain J Vijn's attribution and the
existing Tonc-based code. The included original-demo track is `careless_whisper.mod`;
its embedded credits mention Basil Fawlty / Scope-1990. This checkout does not
supply a project license or complete artwork/music permissions. Existing credits
and assets are retained; no new third-party license grants are inferred.
The new Cream ROM, source song archive, audio and chart are not included in the
public Mission 009 review bundle.
