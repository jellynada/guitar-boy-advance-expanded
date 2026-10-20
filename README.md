# Mission 015 foundation work

Repository audit and CI development-artifact workflow are prepared on
`foundation-audit-2026-10-20`. See [audit and backlog](docs/MISSION_015_FOUNDATION_AUDIT.md)
and [build/download procedure](docs/MISSION_015_BUILD_DELIVERY.md). GitHub publication,
real downloads, licensing and physical-hardware acceptance remain separate gates.
The runtime remains the provisional M014 engine; no gameplay is changed.

# Mission 014 — provisional pause/resume review

Imported Easy uses **LEFT / B / A**. Press **START** to pause/resume; **SELECT** exits while paused. START+SELECT returns to the selector. Original Demo controls remain unchanged.

Mission013 handheld acceptance is still pending; the owner authorized this provisional work. See [Mission014 details](docs/MISSION_014_PAUSE_RESUME.md) and the [handheld checklist](docs/OWNER_M014_PLAYTEST.md). Public download contains synthetic audio only. The actual Cream ROM is kept local, as requested, until authorized private delivery exists. There is no working private attachment tool in this session.

# Guitar Boy Advance Expanded — Mission014 provisional review

A Game Boy Advance rhythm game based on
[startfliing's original project](https://github.com/startfliing/guitar-boy-advance).
The working engine has imported Easy charts/audio, reactive guitar muting,
score/combo, sustains, results/replay, an input diagnostic and the repaired
perspective highway. Mission013 corrects imported Easy physical controls to LEFT/B/A. Charts, audio,
timing and scoring rules are preserved. **Development review baseline, not a stable public release.**

## Play the public test on Windows

[Download the public Mission014 review ZIP](https://raw.githubusercontent.com/jellynada/guitar-boy-advance-expanded/refs/heads/mission-014-download/downloads/mission014-review.zip).

1. Right-click the ZIP → **Extract All**.
2. Install [mGBA for Windows](https://mgba.io/downloads.html).
3. File → Load ROM → **Guitar-Boy-Advance-M014-Synthetic.gba**.
4. Confirm **M014 / SYNTH**, choose Imported Easy Test, or INPUT / CHORD TEST.

The short public imported song uses original synthetic audio/chart data. The
existing Original Demo is retained with its inherited assets and699-note chart.

## Optional developer build (launcher preserved)

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
Follow its prompts, including release-B/keep-A. Missing held keys may indicate
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
python3 tools/package_public.py --build builds/public/VERSION --output builds/public/packages/mission014-review.zip
```

Host QA needs g++, Python3, FFmpeg and NumPy: `bash tests/check.sh`.
mGBA C regressions additionally need gcc/libmgba-dev. Official profiles always
build fresh committed source (or verify the complete exported source manifest),
validate inputs and publish versioned outputs with manifests. FFmpeg version can
change conversion bytes. Actual Windows launcher execution is not claimed from
this Linux workspace; see the Mission014 report for performed checks/limits.

## Project and review status

Mission014 is provisional on Mission013, whose LEFT/B/A handheld acceptance is
unconfirmed. No merge into develop/main. Both real Cream and synthetic profiles
build;37 behavior/input regressions,42 pause cases and Original Demo checks pass.
The established Cream scoring reference remains15815. One strict mGBA0.10.1
common-backing output comparison remains open despite passing exact mixer bytes;
see [the full evidence and limits](docs/MISSION_014_PAUSE_RESUME.md).

Cream ROM delivery is blocked because no supported private upload route is
available. The owner asked to keep it local; no public encrypted Cream ZIP is
created for download. [Owner handheld checks](docs/OWNER_M014_PLAYTEST.md) and
explicit integration approval remain required. No Mission015 work is included.
See [branch policy](docs/RELEASE_PROCESS.md), [known issues](docs/KNOWN_ISSUES.md)
and [future design](docs/DESIGN_BACKLOG.md).

## Credits and inherited content

Original Guitar Boy Advance by startfliing; Tonc, Maxmod and devkitPro retain their
respective attribution/licensing requirements. Existing demo music, chart and art
are retained under their historical arrangement; separate redistribution review
is outstanding and no repository-wide LICENSE was found. Historical public song
downloads also require review. Mission013 adds no public third-party song package.
