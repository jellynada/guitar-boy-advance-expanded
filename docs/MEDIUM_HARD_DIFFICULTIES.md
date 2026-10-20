# Custom-song difficulty selection

Custom-song selection now opens a separate difficulty menu. UP/DOWN chooses an
available native chart; A/START starts; B/SELECT returns to song selection.
Unavailable difficulties are omitted. Original Demo keeps its existing flow.
Results replay the selected chart; exiting returns to song selection. Imported
START pause/resume and paused SELECT exit are unchanged.

| Difficulty | Native lanes left to right |
| --- | --- |
| Easy | LEFT, B, A |
| Medium | LEFT, RIGHT, B, A |
| Hard | LEFT, UP **or** DOWN, RIGHT, B, A |

UP and DOWN are OR aliases of Hard lane2. Edges are computed after logical
coalescing: adding the other alias or releasing one while the other remains
held does not create a hit/release. No configuration change is needed. New
frets held across pause/resume remain seeded without phantom hits. The input
chord diagnostic remains the existing Easy diagnostic, not a new five-lane UI.

## Build a custom ROM

The generic pipeline now defaults to `--difficulty All`: it prepares the native
Easy/Medium/Hard lead-guitar charts present in the package, sharing the same
converted audio. `--difficulty Easy`, `Medium` or `Hard` builds a single available
choice instead. No chart is relabelled, dropped or converted from Expert.

```sh
python3 tools/song_pipeline.py YOUR_PACKAGE.zip --guitar guitar.opus --backing song.opus --output imports/output/custom-menu --difficulty All
python3 tools/build_profile.py song --input imports/output/custom-menu
```

Use the actual audio filenames in your package. Fixed mix is also supported
with repeated `--mix FILE`; it has no reactive guitar muting. The original
public and Cream regression profiles retain their original Easy fixture/header
bytes, but now show a one-choice difficulty screen. Existing private ROMs and
archives are never rewritten.

Menu preparations use `gba-prepared-song-v2`; single-chart preparations retain
v1. v2 records available difficulties, per-chart controls/counts and maximum
runtime capacity. Notes/holds remain in ROM for each chart; bounded judgment,
score and sustain state are reused for the selected chart. There is no heap
allocation, duplicate audio, runtime ZIP reader or SD song loader. The original
max-capacity ROM/ELF guard is preserved; source/chart/audio hashes bind the bundle.

Generate a new original test package with all three charts:

```sh
python3 tools/generate_difficulty_example.py builds/difficulty-examples
python3 tools/song_pipeline.py builds/difficulty-examples/pulse --mix melody.wav --output imports/output/difficulty-test --difficulty All
python3 tools/build_profile.py song --input imports/output/difficulty-test
```

## Limits and acceptance

Native lanes must fit the selected difficulty (3/4/5); incompatible shapes fail
rather than losing notes. The existing32-visible-head and8192-per-chart parser
bounds, PCM/ROM limits and clock/judgment/scoring rules remain. More lanes do
not establish that every high-density chart fits GBA CPU/RAM/OAM budgets.
Native LEFT+RIGHT chords may be physically impractical on the conventional D-pad;
notes are not silently remapped to avoid them. Owner hardware playtesting remains
necessary for chord ergonomics, five-lane spacing, sound and cartridge behavior.
The known strict emulator audio comparison issue remains open; no threshold is
relaxed by this change. No public release or integration into main/develop is
part of this implementation.
