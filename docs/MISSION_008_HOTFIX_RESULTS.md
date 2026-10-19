# Mission 008 hotfix validation — 2026-10-19

## Build and preserved content

Actual Cream ROM: `Sunshine-of-Your-Love-Mission-008-Hotfix.gba`.
Native devkitARM build command (using the existing locally prepared song):

```sh
export DEVKITPRO=/workspace/.cloud-setup/gba/devkitpro
export DEVKITARM=$DEVKITPRO/devkitARM
export PATH=$DEVKITARM/bin:$DEVKITPRO/tools/bin:$PATH
make -j2 IMPORTED_HEADER=imports/output/mission008/imported_chart.hpp AUDIO_DIR=imports/output/mission008/audio
```

Synthetic ROM: `Guitar-Boy-Advance-Mission-008-Hotfix-Synthetic.gba`.
Run `make -j2` without private overrides to build the synthetic 25-note exercise.
Do not confuse it with the actual Cream ROM.

The ROM arrays were extracted using matching ELF symbol addresses and compared
to the previous Mission 008 ROM. All 395 notes (6,320 bytes) and both 4,436,336-byte
PCM streams are byte-identical. No audio playback/gate or scoring rule changes.

| Content | SHA-256 (unchanged) |
| --- | --- |
| 395 notes | 946ab6b383c2a6a75207904abbc0ddbb4a84aaf57cbb6a7bae86e4aa00f974db |
| Guitar PCM | f0dd9ae3ffc3c04efc292ef815652a792dde2914880480efd4c94581595908fc |
| Backing PCM | 0efd813e88652191bfcd0574d59d6d96ec4d52e81484ca5b31a44956003db764 |

## Real song: full start-to-end runs

Linux mGBA 0.10.1 library; 16,400 frames/run (about 274 seconds), real 395-note
Cream chart, full recording through audio EOF and complete results. Each run
asserted composed HUD digits, composed results, frozen final score, replay/reset,
and four additional Original/Imported mode-switch cycles. B and Select menu
return and A and Start replay were separately exercised. Replayed audio advanced
past 16,000 samples; the displayed score reset to zero.

| Run | Final statistics |
| --- | --- |
| perfect | score15230 combo395 maximum395 highest4 accuracy10000 FC1 AP1 session1 |
| good | score7615 combo395 maximum395 highest4 accuracy10000 FC1 AP0 session1 |
| miss | score0 combo0 maximum0 highest1 accuracy0 FC0 AP0 session1 |
| scoring | score2465 combo0 maximum3 highest1 accuracy7494 FC0 AP0 session1 |
| wrong | score3835 combo0 maximum2 highest1 accuracy10000 FC0 AP0 session1 |
| reactive | score2630 combo0 maximum2 highest1 accuracy6658 FC0 AP0 session1 |
| returnmenu | score0 combo0 maximum0 highest1 accuracy0 FC0 AP0 session1 |
| returnselect | score0 combo0 maximum0 highest1 accuracy0 FC0 AP0 session1 |
| replaystart | score0 combo0 maximum0 highest1 accuracy0 FC0 AP0 session1 |

Accuracy is in hundredths of a percent. Dynamic mixed/wrong inputs can land on
different sides of the unchanged Perfect/Good boundary as foreground timing
changes; each score is independently rebuilt from actual judgment events.
Perfect = 15,230; Good = 7,615; Miss = 0. Normal runs report zero underruns.
Repeated pixel checks include quiet intervals, score changes, combos and
multipliers; final pixel checks cover all requested statistics and instructions.
Native unedited screenshots are in `screenshots/mission008-hotfix/`.

## Regression checks

- `bash tests/check.sh`: all 93 Python tests and all C++ ASan/UBSan tests passed,
  including the new 120-frame bounded EOF diagnostic checks.
- Original Demo: 36,000 frames each; 699 Perfect, 699 Miss, and mixed
  59 Perfect / 118 Good / 522 Miss / 1,200 wrong inputs; original sound and
  perspective feedback retained, no core crash.
- Synthetic full runs: Perfect, Good, Miss, mixed, reactive, wrong, replay A/Start,
  menu B/Select; visible results and numerical statistics checked.
- Synthetic audio timer/DMA/sound/IRQ/underrun faults and inconsistent data:
  retain interrupted/error states without completion awards.
- Deliberately hiding the HUD makes the new test fail on an invisible S;
  hiding results makes it fail on an invisible R. Internal counters alone no
  longer satisfy display acceptance.
- A test sampling issue initially caused synthetic wrong-input checks to find
  too few quiet sample frames: sampling every 60 frames coincided with wrong
  input every 30 frames. Sampling every 61 frames resolves the aliasing without
  weakening the glyph assertions.

## Audio validation: passes and an unresolved failure

After correcting the pre-start capture-clock wrap described in the findings,
independent waveform checks pass for real-song Perfect, Good, Miss, reactive
hit/miss, and wrong-input runs. They compare beginning/middle/end synchronization,
steady backing-only intervals, and guitar fade/recovery. There is no captured
clipping or normal-run underrun in those passed analyses. Audio code and PCM
arrays remain unchanged.

**One additional mixed-scoring waveform analysis remains failed**: its guitar-on
window at approximately 159.463 seconds correlates 0.67024 against the independent
model, below the existing 0.94 threshold. Beginning/middle/end synchronization
checks passed before that failure. The threshold was not relaxed and this run
is not counted as passing. Mixed-scoring display/completion/navigation checks
passed. Other two mixed reactive/wrong waveform runs passed their full models.
This discrepancy is unresolved; the build is a review/playtest candidate, not a
claim that every regression check passed. No speculative audio changes were
made outside this HUD/completion mission.

## Remaining acceptance limits

The original owner-reported end-screen failure is not reproduced in this Linux
mGBA core, and no definitive root cause is claimed. These automated checks prove
that the new delivered ROM displays the HUD and results and navigates in this
core; they do not establish why the older Windows playtest failed. There was
no human keyboard playthrough/listening test or physical GBA test. Windows mGBA
manual acceptance and investigation of the one audio comparison remain open.
The hotfix is **not marked fully accepted** pending those checks.

## Delivered ROM hashes

- Cream: 9,163,352 bytes; SHA-256 `5a96221dcc74df8905f3beeba70115c8287d99db048acb4b6c0238b983ff85e0`.
- Synthetic: 803,396 bytes; SHA-256 `bd4ced3a9d801d5835059ce60db4a8a2969a4253dfd183bc6462257e562eded5`.
