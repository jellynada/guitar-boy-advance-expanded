# Guitar Boy Advance Expanded — Mission 010 review candidate

A Game Boy Advance rhythm game based on
[startfliing's original project](https://github.com/startfliing/guitar-boy-advance).
Mission010 adds an isolated input/chord diagnostic and stronger build/graphics
checks. **Owner acceptance is pending; one strict audio-analysis check is still
failing. This is not a stable release.** Main has not been merged.

## Download and play on Windows 11

[**Download the public Mission 010 review ZIP**](https://raw.githubusercontent.com/jellynada/guitar-boy-advance-expanded/refs/heads/mission-010-download/downloads/mission010-review.zip).

1. Download, right-click the ZIP and select **Extract All**.
2. Install [mGBA for Windows](https://mgba.io/downloads.html).
3. In mGBA choose **File → Load ROM** and open
   **Guitar-Boy-Advance-Mission-010-Synthetic.gba**.
4. Check that the selector says **M010 QA**. Up/Down selects; A/Start begins.

**INPUT / CHORD TEST** checks simultaneous buttons, missing/extra inputs, rapid
presses and overlapping holds. It is silent, original diagnostic data, separate
from the real song. Watch the countdown and follow the on-screen instructions.
GBA HELD shows received inputs; EXPECTED shows the target; HEAD HIT/NOT HIT and
PASS/PARTIAL/MISS/WRONG/HOLD FAIL show what registered. LAST PRESS keeps brief new
presses readable. [Full instructions and keyboard tips](docs/QA_TEST_PLAN.md).

**Imported Easy Test** is the short synthetic song (25heads, six holds), not the
Cream recording. **Original Demo** keeps the original music/art and699notes.

- Easy lane order: **GBA Left / A / B**.
- Original lane order: **GBA Left / Right / A / B**.
- **Start+Select** returns to selection during play or diagnostics.
- Song results: **A/Start** replays; **B/Select** returns to selection.
- Diagnostic final summary: **A/Start** retries; **B/Select** exits.

These are GBA button names. Check mGBA Settings → Controllers for keyboard
mappings. Some keyboards drop simultaneous keys; try GBA Left/A/B on J/K/L or
use a controller before concluding that the game missed a physical press.

Scoring is unchanged: Perfect10/Good5times multiplier;2x/3x/4x at10/20/30hits;
Miss/WrongInput reset combo and mute guitar; Perfect/Good restore guitar; backing
continues. Sustains earn1base point per completed250ms at the head's captured
multiplier. Early release stops future bonus, keeping prior points/combo/guitar.

## Your Cream song

The existing owner ZIP was used to build the full recording with395Easy heads
and78sustains. Ten full-song gameplay scenarios pass; the mixed reactive waveform
analysis has one unresolved window at232.665s. Do not treat this as stable signoff.
There is no verified private chat-file uploader here. Mission010 does not publish
new third-party recordings/chart data; historical public Cream builds need a
separate permissions review.

[Windows11 one-time setup and local build guide](docs/RELEASE_PROCESS.md#windows-11--build-the-owners-cream-zip-locally).
After WSL/Ubuntu, Docker Desktop and FFmpeg setup, put the owner's ZIP in the
source folder as `Cream.zip`. Run these two commands in Ubuntu from that folder:

```bash
python3 tools/prepare_song.py Cream.zip --reactive --guitar-stem guitar --backing-stem rhythm --backing-stem song --output-dir imports/output/mission010
bash scripts/build-docker.sh "IMPORTED_HEADER=imports/output/mission010/imported_chart.hpp" "AUDIO_DIR=imports/output/mission010/audio"
```

Continue only if both succeed. Open **guitar-boy-advance-expanded.gba** in that
source folder. Check **M010 QA / LOCAL / AUDIO**, select Imported Easy Test, and
start fresh without an old save state. The public build says SYNTH / AUDIO.
The commands were exercised in a clean Linux export and reproduced the private
ROM byte for byte here; Windows installation and human play were not tested.

## Developer build and evidence

C++, devkitARM, Tonc, Maxmod and Grit; pinned Docker image in
`scripts/build-docker.sh`. Public default: `bash scripts/build-docker.sh`.
Native: set DEVKITPRO/DEVKITARM, add their bin directories to PATH, then `make -j2`.
GNU Make4.3+, Python3 and a host C++ compiler are needed; FFmpeg for song conversion.
The host converter is compiled from source; retained Windows converter EXEs are
not used. Make generates note.h, chart/graphics/audio headers, assembly, soundbank,
ELF and ROM. Cream.zip, imports/output and build products stay ignored.

`bash tests/check.sh`:98Python tests and8C++ sanitizer programs. With libmgba-dev
and DEVKITARM, `bash tests/run_input_emulator.sh perfect /tmp/input` checks actual
composed diagnostics; existing audio/original runners remain available. Builds
and supported runners reject mismatched ROM/ELF and chart counts.
See [QA matrix](docs/QA_TEST_PLAN.md), [stabilization evidence](docs/MISSION_010_STABILIZATION.md),
[known issues](docs/KNOWN_ISSUES.md), [release/consolidation plan](docs/RELEASE_PROCESS.md),
[project architecture/status](docs/PROJECT_STATUS.md),
[sustain rules](docs/SUSTAIN_GAMEPLAY.md) and [importer guide](docs/CHART_IMPORT_GUIDE.md).
[Review source changes](https://github.com/jellynada/guitar-boy-advance-expanded/compare/mission-009-sustain-gameplay...mission-010-stabilization).

## Credits and asset rights

Original game: startfliing. Mode7 files retain J Vijn's Tonc-based attribution.
Original-demo careless_whisper.mod credits Basil Fawlty / Scope-1990. No project
LICENSE or complete art/music permissions were found. Preserve assets/credits;
no third-party redistribution rights are inferred. Public review additions use
synthetic chart/audio and retain the unchanged original demo. No new Cream ROM,
source ZIP, audio or chart is included in the Mission010 public review package.
