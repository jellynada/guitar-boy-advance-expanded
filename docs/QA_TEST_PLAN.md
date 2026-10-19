# Mission 010 QA and owner playtest

## Windows 11 — no programming needed to play the public build

1. Download the Mission 010 review ZIP linked in README. Right-click → Extract All.
2. Install mGBA from https://mgba.io/downloads.html (Windows 64-bit installer).
3. In mGBA choose File → Load ROM and open `Guitar-Boy-Advance-Mission-010-Synthetic.gba`.
4. Confirm the selector says **M010 QA**. Up/Down selects; A or Start begins.
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
- [ ] Report graphical glitches with song time; confirm whether they hide notes.
- [ ] Specifically listen around 3:52–3:54 of runtime for the open audio-analysis issue.

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
python3 tests/analyze_sustains.py --adapted imports/output/mission010/adapted.json --prefix /tmp/cream-holds --log /tmp/cream-holds.log
python3 tests/analyze_reactive.py --audio-dir imports/output/mission010/audio --prefix /tmp/cream-reactive --times 6.321990966796875,135.0880126953125,264.8800048828125 --require-mute --require-recovery
```

Current strict reactive command fails at fade-down232.665039s; keep that result.
Seven other real primary waveform scenarios pass. The optional additional
`--backing-capture /tmp/cream-miss` comparison fails in the scoring scenario at
46.137634s against its >0.999 common-filter threshold; it is not the M009 primary
acceptance invocation. No thresholds or playback rules were changed.

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

Native240x160 PNGs in screenshots/mission010 are converted from actual final
mGBA PPM frames, without redrawing or enlarging them. Coverage includes selector,
start, dense passage, head judgment, hold onset/bonus/active/release/completion,
EOF, visible results, replay and diagnostics. Private Cream captures remain local.
The comparison silent frame uses the same synthetic chart but a different clock
path; it is supporting evidence, not a pixel-identical controlled timing test.
An isolated (unshipped) probe counted HBlank entries outside hardware HBlank:
12,994/215,553 audio versus1/200,878 silent, including navigation. It adds a few
instructions to IRQ entry; no probe instrumentation is in the delivered ROM.
EOF/results transitions are checked on composed output after state settles,
not merely on a completion counter. All masks/affines/resources are audited;
hardware scanline timing and stack high-water testing remain outstanding.
