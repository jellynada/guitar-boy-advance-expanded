# Guitar Boy Advance Expanded — Mission013 development foundation

A Game Boy Advance rhythm game based on
[startfliing's original project](https://github.com/startfliing/guitar-boy-advance).
The working engine has imported Easy charts/audio, reactive guitar muting,
score/combo, sustains, results/replay, an input diagnostic and the repaired
perspective highway. Mission013 corrects imported Easy physical controls to LEFT/B/A. Charts, audio,
timing and scoring rules are preserved. **Development review baseline, not a stable public release.**

## Play the public test on Windows

[Download the public Mission013 review ZIP](https://raw.githubusercontent.com/jellynada/guitar-boy-advance-expanded/refs/heads/mission-013-download/downloads/mission013-review.zip).

1. Right-click the ZIP → **Extract All**.
2. Install [mGBA for Windows](https://mgba.io/downloads.html).
3. File → Load ROM → **Guitar-Boy-Advance-M013-Synthetic.gba**.
4. Confirm **M013 / SYNTH**, choose Imported Easy Test, or INPUT / CHORD TEST.

The short public imported song uses original synthetic audio/chart data. The
existing Original Demo is retained with its inherited assets and699-note chart.

## Build your Cream ROM locally

Keep your existing song ZIP separately; you do not need to edit game code.
Follow [one-time Windows setup](docs/WINDOWS_PRIVATE_BUILD.md), place your ZIP at
**private/Cream.zip**, then double-click **Build-Cream-ROM.bat**. The launcher
builds the same engine using the actual recording,395 Easy notes and78 sustains.
It prints the new ROM location and checksum. Nothing is uploaded. Private
inputs/outputs are ignored by Git and excluded from public review packages.

## Controls

Imported Easy uses **GBA Left / B / A** from left to right. Original
Demo uses **Left / Right / A / B**. Check mGBA Settings → Controllers for your
keyboard mappings. Medium/Hard mappings remain future work.
Up/Down selects modes; A or Start begins. Start+Select exits play. Results:
A/Start replays; B/Select returns. A held button sustains its matching note;
release early to lose later hold bonuses. Misses mute the guitar; backing continues.

INPUT / CHORD TEST automatically walks through single buttons, chords and holds.
Follow its prompts, including release-A/keep-B. Missing held keys may indicate
keyboard ghosting; try a different mapping/controller. See docs/QA_TEST_PLAN.md.

## Build and test for developers

Official builds need Python3 and Docker. Only private conversion needs host
FFmpeg. The pinned toolchain includes C++17 devkitARM, Tonc, Maxmod and the native
chart converter; the included historical Windows converter is not executed.

```bash
python3 tools/build_profile.py public
# Optional, with your own private/Cream.zip:
python3 tools/build_profile.py cream
# Public ZIP; use the successful versioned folder printed by the first command:
python3 tools/package_public.py --build builds/public/VERSION --output builds/public/packages/mission013-review.zip
```

Host QA needs g++, Python3, FFmpeg and NumPy: `bash tests/check.sh`.
mGBA C regressions additionally need gcc/libmgba-dev. Official profiles always
build fresh committed source (or verify the complete exported source manifest),
validate inputs and publish versioned outputs with manifests. FFmpeg version can
change conversion bytes. Actual Windows launcher execution is not claimed from
this Linux workspace; see the Mission013 report for performed checks/limits.

## Project and review status

Mission013 handheld acceptance is pending your personal LEFT/B/A playtest.
The owner reports Mission011 runs well on actual GBA: flicker gone, good music,
working score/holds/results/replay. This is valuable scoped acceptance, not full
hardware certification. Two strict additional mGBA audio comparisons, physical
DMA margins and stack measurements remain open. No thresholds were relaxed.

Source is saved on mission branches; develop is the integration baseline.
Mission013 is isolated from the Mission012 develop baseline; no merge is performed.
Main remains historical until explicit owner approval. Download branches never
merge into source. See [release/branch policy](docs/RELEASE_PROCESS.md),
[Mission013 evidence](docs/MISSION_013_PHYSICAL_CONTROLS.md),
[known issues](docs/KNOWN_ISSUES.md) and [future design](docs/DESIGN_BACKLOG.md).

## Credits and inherited content

Original Guitar Boy Advance by startfliing; Tonc, Maxmod and devkitPro retain their
respective attribution/licensing requirements. Existing demo music, chart and art
are retained under their historical arrangement; separate redistribution review
is outstanding and no repository-wide LICENSE was found. Historical public song
downloads also require review. Mission013 adds no public third-party song package.
