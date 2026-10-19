# Guitar Boy Advance Expanded — Mission 011 review candidate

A Game Boy Advance rhythm game based on
[startfliing's original project](https://github.com/startfliing/guitar-boy-advance).
Mission011 repairs imported highway scanline timing. **Outcome B:** graphics repair
is verified, but emulator audio compatibility and owner acceptance still block a
stable release. Main remains unchanged.

## Download and play on Windows 11

[**Download the Mission 011 public review ZIP**](https://raw.githubusercontent.com/jellynada/guitar-boy-advance-expanded/refs/heads/mission-011-download/downloads/mission011-review.zip).

1. Download, right-click the ZIP and choose **Extract All**.
2. Install [mGBA for Windows](https://mgba.io/downloads.html).
3. In mGBA choose **File → Load ROM** and open
   **Guitar-Boy-Advance-Mission-011-Synthetic.gba**.
4. Check **M011 TIMING**. Up/Down selects; A/Start begins.

**Imported Easy Test** plays the short original synthetic song, not Cream.
**INPUT / CHORD TEST** checks simultaneous buttons and overlapping holds using
original silent test data. **Original Demo** preserves the existing music/art
and699notes. [Complete playtest checklist](docs/QA_TEST_PLAN.md).

- Easy lane order: **GBA Left / A / B**.
- Original lane order: **GBA Left / Right / A / B**.
- **Start+Select** returns to selection during gameplay or diagnostics.
- Song results: **A/Start** replays; **B/Select** returns to selection.
- Diagnostic summary: **A/Start** retries; **B/Select** exits.

These are GBA button names. Check mGBA Settings → Controllers for your keyboard
mapping; try GBA Left/A/B on J/K/L or a controller if your keyboard drops chords.
The diagnostic distinguishes GBA HELD, NEW/LAST PRESS, EXPECTED, HEAD HIT/NOT HIT
and VALID HOLD. Follow its countdown; deliberately omit a chord button to confirm
PARTIAL/MISS rather than PASS. All judgment/scoring/hold rules remain unchanged.

## What was verified, and what remains open

The repaired real-song build had zero displaced-floor detections across16086
checked gameplay frames, zero late scanline writes and no ordinary audio underruns.
The entire395-note/78-sustain reference chart still completes; all-Perfect holds
score15815.108Python tests and8C++ sanitizer programs pass, plus full-song,
original-demo, input, error, replay/menu and framebuffer regressions.

All8primary real audio waveform models pass unchanged limits. Two additional
strict comparisons still fail in the unmodified test emulator. Exact FIFO data
is correct, and a controlled emulator-only timestamp correction explains the
failures. That correction is not shipped or silently used for acceptance.
Windows human listening/playing and physical GBA testing remain pending.
[Evidence and performance](docs/MISSION_011_AUDIO_GRAPHICS.md) ·
[Known issues](docs/KNOWN_ISSUES.md).

[Native before/after graphics comparison](docs/screenshots/mission011/comparison.html)
is included in the ZIP: open it in Edge/Chrome to view the synthetic animations.
The individual images are native240x160frames. No real Cream images/audio/chart
package is published in this review build.

## Your Cream song

The real recording and all395Easy heads/78sustains were built and verified privately.
No supported private attachment uploader is available here. Mission011 authorizes
synthetic public review material; it does not authorize a new public Cream ROM.
The existing owner ZIP and reproducible local build remain available.

Follow the [Windows11 setup/build guide](docs/RELEASE_PROCESS.md#windows-11--build-the-owners-cream-zip-locally).
After one-time WSL/Ubuntu, Docker Desktop and FFmpeg setup, put the owner's archive
in the source folder as `Cream.zip`, then run these two commands in Ubuntu there:

```bash
python3 tools/prepare_song.py Cream.zip --reactive --guitar-stem guitar --backing-stem rhythm --backing-stem song --output-dir imports/output/mission011
bash scripts/build-docker.sh "IMPORTED_HEADER=imports/output/mission011/imported_chart.hpp" "AUDIO_DIR=imports/output/mission011/audio"
```

Continue only if both commands succeed. Open **guitar-boy-advance-expanded.gba**
in that source folder; confirm **M011 TIMING / LOCAL / AUDIO**, then choose
Imported Easy Test. Start fresh without an old save state. A default public
build says SYNTH / AUDIO. The two commands reproduced the private ROM byte for
byte in a clean Linux export; Windows installation/GUI was not tested.

## Developer build and QA

C++, devkitARM, Tonc, Maxmod and Grit remain the engine/toolchain. Public build:
`bash scripts/build-docker.sh` (official image pinned by digest). Native build:
set DEVKITPRO/DEVKITARM, add their bin directories to PATH, then `make -j2`.
Native prerequisites: GNU Make4.3+, Python3, desktop C++ compiler and devkitPRO
libraries/tools. FFmpeg is needed for private conversion. NumPy/libmgba are QA
requirements, not ordinary ROM-build requirements.

Make compiles the host chart converter; retained Windows EXEs are not used.
note.h, chart assembly, graphics/audio headers, soundbank, ELF and ROM are generated.
Builds verify chart/hold/EOF bounds, cartridge size, ROM/ELF equality and note count.
Cream.zip, generated imports and ROMs remain ignored in source branches.

`bash tests/check.sh` runs108Python tests and8C++ sanitizer programs (NumPy and
FFmpeg required for the full host QA suite). libmgba-dev and DEVKITARM enable
headless rendered-game checks. New host-only tools distinguish exact digital PCM,
actual PWM/resampler output, scanline timing and final pixels. The optional
emulator correction is strictly a developer experiment. Normal tests do not use it.

Read [QA commands](docs/QA_TEST_PLAN.md), [architecture/status](docs/PROJECT_STATUS.md),
[release/Windows guide](docs/RELEASE_PROCESS.md), [sustain rules](docs/SUSTAIN_GAMEPLAY.md)
and [chart importing](docs/CHART_IMPORT_GUIDE.md).
[Review Mission011 source](https://github.com/jellynada/guitar-boy-advance-expanded/compare/mission-010-stabilization...mission-011-audio-graphics-stability).
No source integration is performed in this mission.

## Credits and asset rights

Original game: startfliing. Mode7 retains J Vijn's Tonc-based attribution.
careless_whisper.mod credits Basil Fawlty /Scope-1990. No project LICENSE or full
music/art permissions were found; preserve original credits/assets and review
rights separately. Public review additions use original synthetic content while
retaining the original demo. Historical public Cream builds require separate
permissions review; no new Cream recording/chart/ROM is uploaded here.
