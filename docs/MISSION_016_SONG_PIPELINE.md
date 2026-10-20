# Mission 016: general song preparation/build foundation

Starting source: `7fee39d93693d4437da188a0b5d9e89e8e9081d2`, new branch
`mission-016-song-pipeline`. Mission015 artifact retrieval and draft PR#2 are
owner-reported complete: https://github.com/jellynada/guitar-boy-advance-expanded/pull/2.
No repeat of its authentication investigation or unchanged ROM builds is needed.

## Assessment and controlled plan

The bounded package/chart/MIDI readers, Easy adapter, host FFmpeg preparation,
pinned compiler and successful-build inventory are reusable. The official driver
has only a fixed public fixture and Cream regression profile; its Cream395-head,
78-sustain and three-stem checks are appropriate fixture assertions, not generic
song acceptance. Existing adapted-v1 descriptive controls predate LEFT/B/A.
Keep those fixtures byte-for-byte stable and introduce an independent versioned
prepared-song contract that describes the actual runtime controls.

Add a `song` build profile, private by default even for caller-supplied synthetic
content. It consumes a verified prepared directory, never changes source code,
and records the song manifest hash alongside source/toolchain/ROM identities.
Use explicit relative audio paths (fixed mix or guitar plus backing), not
Cream stem names. Bind normalized source, adaptation, chart header and audio
with hashes; validate onset and genuine-sustain end alignment. Reject malformed,
unsupported, ambiguous or incompatible data instead of repairing it.

First prove two generated original packages: constant-tempo chart/fixed mix and
tempo-changing MIDI/reactive audio, with different titles, counts, lengths and
sustains. Generate WAV audio locally; do not commit binaries/recordings. Reuse
existing actual-key emulator tests with metadata-derived song counts/duration.
No runtime, judgment, audio clock, mixer, renderer or gameplay changes are needed.
Keep public packaging restricted to the original public fixture. No publication,
merge or stable release is part of this mission.

## Supported input and runtime subset

- ZIP (stored/deflated) or extracted Clone Hero-style song folder. `.chart`,
  `.mid` and `.midi` files can be selected directly when their sibling audio/INI
  files are present; use `--chart RELATIVE_PATH` for multiple charts.
- Existing bounded chart parser and Standard MIDI File type0/type1 PPQ parser.
  Tempo changes, exact/rational normalization and explicit chart/INI offsets
  remain unchanged. Nonzero conflicting chart Offset and INI delay require
  `--offset-policy add`, `ini` or `chart`. No guessed timing repairs.
- Host FFmpeg/ffprobe decodes WAV, OGG, MP3 and OPUS through the existing codec
  allowlist. One audio stream/file; explicit relative filenames must be beside
  the selected chart. Preview is rejected. Maximum8 selected files. Fixed mix
  averages selected files; reactive mode separates one guitar from1..7 backing
  files. Shorter stems zero-pad as before; assigning instrument roles is a user
  decision, not automatic separation.
- Exactly one compatible Easy five-fret lead-guitar track, native lanes0/1/2
  mapped to LEFT/B/A. Existing1..8192 notes and32-visible-head limit apply.
  Other difficulties/instruments are retained in normalized data but cannot be
  selected for gameplay. Open/rewritten/incompatible lanes and duplicate same-
  lane onsets fail instead of being dropped or collapsed. Source modifiers,
  phrases and INI rule overrides are retained; no HOPO/strum/phrase gameplay.
- Existing genuine-sustain policy is unchanged: duration >=ceil(PPQ/3), with
  original durations retained. All onsets and genuine sustain ends must fit the
  decoded source audio. Actual audible synchronization still needs listening
  and hardware playtesting; matching lengths alone do not prove correct audio.
- Existing16,384Hz signed8 mono PCM, two-second pre-roll, half-second tail and
  one-second guard. No compression, runtime decoder, SD song loader, new
  difficulties or song library.30MiB prepared audio and32MiB cartridge limits
  still apply. Static per-note RAM and worst-case hardware budgets need review
  for larger imports;8192 is a parser bound, not a hardware acceptance promise.

## Versioned prepared-song contract

`gba-prepared-song-v1` lives in `song-manifest.json`:

| Field | Contract |
| --- | --- |
| schema_version/status/distribution | Exact supported version, successful preparation, always `private-only` |
| source | Chart/MIDI format; hashes of selected original chart, optional INI and audio; canonical selected-content tree hash. Unused package media are not fingerprinted or copied. |
| selection | Explicit chart path, fixed mix or guitar/backing assignments, offset policy |
| normalized | `gba-song-data-v1` schema and exact normalized timing/offset metadata |
| runtime | Easy lead-guitar selection, actual LEFT/B/A controls, derived note/sustain counts |
| audio | Fixed/reactive mode, sample rate/counts, FFmpeg version |
| file_sha256 | Exact inventory and hashes of normalized data, adaptation, header, prepared PCM/audio metadata and validation reports |

The normalized source (`normalized-song.json`), adapted events (`adapted.json`),
C++ header and audio remain separate. The wrapper corrects descriptive adapter
metadata to actual controls without changing legacy adapter output or its fixture
hashes. Preparation writes into a new output directory only; existing success
is never overwritten. Failure produces an invalid report and no valid manifest.
The build profile verifies the complete package, reconstructs adaptation/header,
checks audio/chart/source bindings and reuses strict PCM validation. It copies
prepared data into the isolated source snapshot, rejects source/input changes
during compilation, and retains prepared provenance with its build result.

Prepared directories reject symlinks, extra/missing files, unsupported schemas,
changed hashes and contradictory metadata. Managed files are bounded to32MiB
per file and32 directory entries. These hashes provide integrity/provenance,
not signatures or permission to distribute recordings. FFmpeg version is recorded;
identical preparation on the same tool version is tested, not cross-version
byte identity. ZIP/folder transport does not confer public-content status.

The existing public profile and public packager still accept only the original
public synthetic fixture. Cream remains its own regression profile with395heads,
78holds and the original explicit stem policy. Generic and Cream results never
enter public CI artifact packaging. All generic ROMs are stored under ignored
`builds/private/songs`; no upload is performed, even for these generated examples.

## Usage (developer backend)

Requires Python3, FFmpeg/ffprobe and the existing pinned Docker compiler image.
The Windows UI is deferred; these backend commands can run in the existing WSL
setup without editing game code. No native Windows execution is claimed.

```sh
# Generate original examples (WAV/chart/MIDI/ZIP files stay in ignored builds/).
python3 tools/generate_song_examples.py builds/song-examples

# Prepare a folder with a fixed mix (no reactive guitar muting).
python3 tools/song_pipeline.py builds/song-examples/pulse --mix melody.wav --output imports/output/pulse-v1
python3 tools/build_profile.py song --input imports/output/pulse-v1

# Prepare a distinct MIDI ZIP with explicit arbitrary stem filenames.
python3 tools/song_pipeline.py builds/song-examples/drift.zip --guitar lead.wav --backing accompaniment.wav --output imports/output/drift-v1
python3 tools/build_profile.py song --input imports/output/drift-v1
```

Each build produces `Guitar-Boy-Advance-M014-Song-Private.gba` and matching ELF in
its own commit/timestamp/unique build directory. The engine label remains honest:
`M014 / SONG / LOCAL`, with the exact source revision embedded. Build manifest
`prepared_song_sha256` binds the versioned preparation manifest. Retain the full
successful directory, not only LATEST.txt: the generic pointer never invalidates Cream selection; both songs have independently retained
ROMs even though that pointer selects just the newest build.

For test execution, generate `nm` symbols from the matching ELF with the pinned
compiler, then run `tools/song_build_smoke.py --build BUILD_DIRECTORY --symbols
SYMBOLS_FILE --output NEW_RESULT_DIRECTORY` on a host with GCC/libmgba. It derives
counts and frame limits from validated song metadata; no6/8/25/395-note assumption
enters production preparation/build logic. Its four existing scenarios exercise
single pause, eight cycles, paused SELECT exit and uninterrupted completion.
They require a song long enough for their scripted pauses; they are example
acceptance tests, not a universal guarantee for every imported chart.

## Remaining dependencies

Finish backend validation before designing a GUI or full Windows installer.
Source inspection diagnostics remain separately scoped in the JSON report;
ready-stage warnings omit discovery-only statements superseded by preparation.
Mission017 requires measured decoder CPU/RAM/quality/clock budgets before any
storage-engine replacement. Larger songs also need explicit static-RAM and
foreground/IRQ budget checks plus physical GBA acceptance. The known strict
emulator common-backing comparison issue remains open with unchanged thresholds.
No hardware acceptance, inherited-asset licensing clearance or public-release
permission follows from these synthetic package tests.

## Verification record

Local host suite:158 Python tests and all10 ASan/UBSan C++ programs passed,
including22 generic pipeline tests. Coverage includes two distinct song models,
WAV/OGG/MP3/OPUS decoding, MIDI tempo/INI offset preservation, repeatable prepared
bytes on the same FFmpeg version, unsupported lanes, unsafe ZIP paths, genuine
sustain/audio bounds, missing/extra/tampered files, schema/metadata binding,
public-artifact rejection and preservation of Cream/failed-build selections.
Existing importer, scoring, input, hold, pause, public-package and release guards
remain in the suite. No source under source/, include/, Makefile, the legacy
adapter or Cream preparation tool is changed.

Pinned ROM compilation and metadata-driven emulator runs are recorded with each
successful local build and smoke receipt. Those are distinct from the host suite;
final execution results must be reported from the actual runs, not inferred from
this record. Generated packages, prepared data, ROMs, ELF files and audio captures
remain ignored/local and are not source commits. Windows and physical GBA
acceptance, the known strict audio issue, and inherited-asset rights stay open.
