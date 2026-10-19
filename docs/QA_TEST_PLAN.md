# Mission 011 QA and owner playtest

## Windows 11 — no programming needed to play the public build

1. Download the Mission 011 review ZIP linked in README. Right-click → Extract All.
2. Install mGBA from https://mgba.io/downloads.html (Windows 64-bit installer).
3. In mGBA choose File → Load ROM and open `Guitar-Boy-Advance-Mission-011-Synthetic.gba`.
4. Confirm the selector says **M011 TIMING**. Up/Down selects; A or Start begins.
5. Choose **INPUT / CHORD TEST** for diagnostics, or Imported Easy Test for the
   short synthetic song. The public build is not the Cream recording.

Easy lane order is **GBA Left / A / B**. Original Demo retains Left / Right / A / B.
In mGBA Settings → Controllers, inspect or change the keyboard mappings. A useful
alternative is GBA Left=keyboard J, GBA A=K, GBA B=L, leaving Up/Down and Start/
Select on separate keys. This changes your keyboard only, not the GBA controls.
Some keyboards cannot send all combinations (ghosting/rollover). If GBA HELD
omits a key you are physically holding, try another mapping or a controller.
The game cannot detect a key that the computer never sends.

### Input test (about 54 seconds)

Thirteen tests run automatically in order with a countdown. Tap at PRESS NOW;
release between distinct notes. The top instruction describes the current test.

| Tests | What to do |
| --- | --- |
| LEFT, A, B | Tap each indicated single button. |
| LEFT+A, LEFT+B, A+B, LEFT+A+B | Press the indicated buttons together. |
| LEFT THEN A | Left at zero, A about half a second later. |
| HOLD LEFT + TAP A | Keep Left held for 1.5s, tap A about 0.75s after onset. |
| HOLD A+B | Hold both for 1.5s. |
| RELEASE A KEEP B | Start both; release A after about 0.5s, keep B for 1.5s. |
| RAPID A A A | Three separate A presses about 0.17s apart. |
| LEFT A B SEQUENCE | Left, A, B about 0.34s apart. |

GBA HELD shows current sampled hardware inputs. NEW PRESS shows the current
poll's edges and may flash briefly; LAST PRESS keeps the last observed edges
readable. EXPECTED is the chart target; HEAD HIT and NOT HIT summarize its lanes.
EVENT LANE and Perfect/Good/Miss/Wrong show gameplay judgments. VALID HOLD shows
buttons currently sustaining valid active notes; BONUS and DONE show progress.
Per-head outcomes still use unchanged normal Easy timing windows, not a relaxed
chord rule. PASS requires every head and required hold outcome, with no extra
press. PARTIAL means some heads registered; MISS means none; WRONG means an
unmatched press; HOLD FAIL means a required hold outcome did not occur. In the
intentional release-A test, an early A release with a completed B hold is PASS.

Start+Select exits at any time. Final summary: A/Start retries, B/Select exits.
Try intentionally omitting a chord button and holding A through the rapid taps:
they should produce PARTIAL rather than PASS. Return to Imported Easy and
Original Demo afterward to check scene/audio reset.

## Owner acceptance — leave unchecked until owner reports results

- [ ] All four chord combinations appear correctly in GBA HELD.
- [ ] Intended chords pass; deliberately omitted/extra inputs do not pass.
- [ ] A+B hold and release-A/keep-B can be observed and understood.
- [ ] Score, combo, multiplier and judgments are readable during the synthetic song.
- [ ] Results show real statistics; A/Start replay starts fresh music; B/Select returns.
- [ ] Original Demo still plays and responds to its four controls.
- [ ] Local Cream build: play the full song, listen for mute/recovery and timing.
- [ ] Cream hold scoring/release behavior feels correct; replay and menu work.
- [ ] Watch the upper highway throughout the full Cream song; report any horizontal displacement with song time.
- [ ] Listen near 2:08, 2:16 and 3:52–3:54; report any crackle, dropout or backing change.

Automated scripts do not constitute owner acceptance. Windows GUI/keyboard and
physical GBA playing were not performed by the agent.

## Developer reproduction

Host prerequisites: Python3, g++, FFmpeg; NumPy for waveform analysis. GBA build:
pinned Docker image in `scripts/build-docker.sh`, or DEVKITPRO/DEVKITARM plus tools
on PATH. mGBA C checks require gcc and libmgba-dev (tested Debian 0.10.1).

```bash
bash tests/check.sh
bash scripts/build-docker.sh
# Native host with libmgba and exported DEVKITARM:
bash tests/run_input_emulator.sh perfect /tmp/input-perfect
bash tests/run_input_emulator.sh partial /tmp/input-partial
bash tests/run_input_emulator.sh wrong /tmp/input-wrong
bash tests/run_input_emulator.sh early /tmp/input-early
bash tests/run_input_emulator.sh stuck /tmp/input-stuck
bash tests/run_audio_emulator.sh sustain-perfect 1800 /tmp/synthetic-holds
bash tests/run_emulator.sh perfect /tmp/original-perfect.ppm 36000
```

Use a separate output prefix for every run. Normal synthetic matrix (1800frames):
sustain-perfect, sustain-release, perfect, good, miss, scoring, wrong, reactive,
returnmenu, returnselect, replaystart; error matrix: fault_dma, fault_sound,
fault_irq, fault_underrun, fault_timer, inconsistent. Original: perfect, miss,
mixed (36000frames each). Input: perfect/partial/wrong/early/stuck.

Private preparation/build commands are in RELEASE_PROCESS. Run the ten full
16400frame real scenarios: sustain-perfect, sustain-release, perfect, good, miss,
scoring, wrong, reactive, returnmenu, returnselect. Preserve matching ROM/ELF,
prepared header and audio; never reuse a ROM after a failed make command.
Make and the supported runners now verify ELF/ROM program+data equality and
compiled note count. `gbafix`'s cartridge-header bytes are excluded intentionally.
Three negative checks rejected wrong count, stale M009 ROM/M010 ELF, and a
one-byte damaged ROM. This safeguard does not certify all cartridge header fields.

```bash
python3 tests/analyze_sustains.py --adapted imports/output/mission011/adapted.json --prefix /tmp/cream-holds --log /tmp/cream-holds.log
python3 tests/analyze_reactive.py --audio-dir imports/output/mission011/audio --prefix /tmp/cream-reactive --times 6.321990966796875,135.0880126953125,264.8800048828125 --require-mute --require-recovery
```

All eight ordinary real primary waveform scenarios now pass the unchanged >0.94
correlation and <1ms error gates. However, the additional >0.999 common-backing
comparison still fails in scoring at135.874939s (0.9976103) and wrong at128.039002s
(0.9988558). Keep both failures visible: **Outcome B, stable promotion blocked**.
The verified Mission010 baseline reproduces its232.665039s failure (0.9099747);
a freshly rerun Mission009 reactive baseline passes. No thresholds were relaxed.

A host-only FIFO observer independently checks exact written and consumed PCM.
It adds no emulated instructions. Example (native libmgba0.10.1, matching build):

```bash
python3 tests/run_hardware_tap.py --rom guitar-boy-advance-expanded.gba --elf guitar-boy-advance-expanded.elf --note-count 395 --prefix /tmp/fifo
python3 tests/analyze_fifo.py --audio-dir imports/output/mission011/audio --prefix /tmp/fifo --startup-advance 15
```

The fixed15sample advance is silent startup priming, not a per-window fit.
Both baseline and repaired real runs have zero digital mismatches. The optional
`--diagnose-fifo-lateness` changes emulator event handling experimentally: it
explains the waveform failures but is **not ordinary acceptance** or a game fix.
See MISSION_011_AUDIO_GRAPHICS for paired, event-identical comparisons.

### Graphics and negative acceptance

`audio_emulator.c` checks composed glyphs for score/combo/multiplier/judgment,
all results labels/values/awards, and fresh replay output. Tail checks combine
actual colored pixels with an independent inverse-perspective lane calculation;
OAM counts alone cannot pass. The input harness drives mGBA hardware keys, checks
sampled masks, actual composed held/valid-hold text, all13 results, retries,
mode switching and fresh original sound. No input/score RAM writes supply PASS.
Error-injection scenarios intentionally write hardware state to test faults.

Environment variables GBA_TEST_HIDE_HUD, GBA_TEST_HIDE_RESULTS,
GBA_TEST_HIDE_TAILS and GBA_TEST_HIDE_DIAGNOSTIC each deliberately hide actual
layers and **must fail**, not exit successfully. All four rejected hidden output.
They are expected failures, separate from QA-010-004's unexpected failure.

Native240x160 PNGs in screenshots/mission011 come from actual emulator output.
Open comparison.html locally to view before/after animations; separate native
frames are in the public ZIP. No redraw, crop or black cover supplies a pass.
Private Cream images, music and chart data remain local.

Reproduce controlled short/long/silent/real/tone/zero/no-tail cases independently:

```bash
python3 tests/run_timing_matrix.py --source-ref 233112a072e5a0e90e5a766207761474130f75a6 --output /tmp/timing-before --private-header imports/output/mission011/imported_chart.hpp --private-audio imports/output/mission011/audio
python3 tests/run_timing_matrix.py --source-ref HEAD --output /tmp/timing-after --private-header imports/output/mission011/imported_chart.hpp --private-audio imports/output/mission011/audio
```

For a shared-workspace Debian container, append
`--emulator-prefix '["docker","exec","mission001-mgba"]'`; otherwise omit it.
The pixel oracle checks actual floor pixels against independent projection and
fog, requiring the road to remain visible. Shifted DMA sources and disabled DMA
must fail. Full repaired Cream playback checks16086 eligible frames: zero bad
pixels and no scanline DMA deadline misses; minimum measured final-write margin
is13 emulated cycles. Before:16085/16085 eligible frames flagged.

The current harness also requires DMA0/3 released on results, diagnostic and
Original scenes. Host suite:108 Python tests plus8 sanitized C++ programs pass;
nine deliberately corrupted digital signals fail and a valid reference passes.
All ten full real scenarios,17 synthetic,5 input and3 long Original runs pass
behavior checks. Full real holds:395 Perfect,78 complete,585 bonus,15815 score.
Early-release script now awards212 bonus versus216 baseline because polling
crosses a quarter-second boundary sooner; independent event reconstruction
confirms212, with unchanged scoring constants. Physical timing, stack high-water,
Windows keyboard/GUI, human listening and owner acceptance remain untested.
