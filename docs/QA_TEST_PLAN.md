# Mission 017 exact-candidate validation

Run tests/check.sh, build_public_demo.py, package_public_demo.py, verify_demo_zip.py,
test_public_demo.py and check_demo_audio.py. Retain all failures; digital accuracy
is not ordinary-output or hardware clearance. Test both hit and mixed graphics
loads, all3 difficulties, aliases, sustains, restart,10s pause/results/replay.
Hash/extract/download back and emulate the exact delivered ROM. See
M017_VERIFICATION.json and OWNER_M017_PLAYTEST.md. Existing host tests and
legacy699-note regressions remain separate; no assertion thresholds relaxed.

# Mission014 additions

## Arcade75 additional gates

Run `bash tests/check.sh`: interval conflicts, protected doubles/triples,
minimal shifts/deletions/failure, occupied/future holds, re-articulation, rapid
transition guards, cutoff boundaries, fade/sample identity, provenance and
repeatable recipes; finite-EOF ASan/UBSan coverage. Keep old full-length tests.
Build real native-All regression and real derived Arcade75-All separately.
Exercise every difficulty, alias handoff, 8 pauses, paused exit, near-EOF pause,
full completion/replay, mixed/miss inputs and Original Demo. Verify graphics,
DMA/IRQ deadlines, stack margin and zero underruns/overflow. Digital mixer
checks and ordinary mGBA output checks are separate; thresholds stay unchanged.
Independent public synthetic packaging must reject any non-generator input,
verify exact extraction and emulate that extracted ROM. AES private packaging
uses independent 7-Zip extraction and matching ROM hashes. A local test is not
a network download or real-GBA acceptance. See ARCADE75_VERIFICATION.md.


Run `bash tests/check.sh`; compile `tests/pause_emulator.c` against libmgba and run `tests/run_pause_matrix.py` with matching profile manifests/symbols. Exercise every case on both actual profiles, including ten minutes, repeated START and both sequential exit orders. Read-only snapshots must freeze sample count, mixer, score, judgments, effects and composed screen. Test current-held resume, independent holds and missing-fret50ms grace. Keep existing uninterrupted regressions/thresholds intact.

Use `tests/hardware_tap.c` with explicit ELF addresses (including GBA_TAP_COUNT_ADDR) and GBA_TAP_SINGLE_PLAYBACK=1 for first-playback pause captures. Run `tests/analyze_pause_audio.py` against matching runtime PCM; no experimental lateness correction. The latter checks declared Timer0 gaps separately, not by relaxing `analyze_fifo.py`. Compare untouched audio/graphics tests, original demo, diagnostic, replay and resources. Owner handheld acceptance remains required; use OWNER_M014_PLAYTEST.md.

# Mission013 physical controls QA

Owner acceptance is **pending** for this mission. Prior Mission011 acceptance
must not be attributed to the new LEFT/B/A mapping. Current automated coverage:
127 Python tests,9 sanitized C++ programs;17 synthetic,10 full real,5 diagnostics
on each profile,3 Original36000frame runs; full real frame oracle and direct
physical/receptor composition tests. See MISSION_013_PHYSICAL_CONTROLS.md for
actual outcomes and the owner checklist.

```bash
bash tests/check.sh
python3 tools/build_profile.py public
python3 tools/build_profile.py cream
# Use each verified profile's matching ROM and ELF-derived symbols:
gcc -O2 -Wall -Wextra -Werror tests/physical_emulator.c -o /tmp/physical -lmgba
/tmp/physical PATH_TO_ROM PATH_TO_NM_SYMBOLS
```

C harnesses use independent physical key bits LEFT32/B2/A1. The old LEFT/A/B
script must fail the new ROM. Check visible LEFT/B/A labels,8 receptor masks,
release-B/keep-A, exact scene tile restoration and Original LEFT/RIGHT/A/B.
Diagnostic live and results labels are verified in actual framebuffer pixels.
Held inputs must not emit repeated NEW PRESS; partial/wrong/early/stuck scripts
remain expected outcome tests. Host tests exhaust1024 hardware masks and8192
logical edge cases plus test-only alias handoffs with no duplicate press/release.
Medium/Hard must remain unavailable as gameplay selections.

Waveform analyzers and thresholds are unchanged. M013 currently passes all eight
primary real models, four synthetic models and three additional >0.999 backing
comparisons. Keep prior M011/M012 failures as compatibility history; do not count
an experimental emulator correction as normal acceptance. No music/timing patch
is used to obtain these passes. All chart/audio hashes match Mission012 exactly.

Delivery verification must download the actual synthetic ZIP and encrypted real
ZIP, reject private payloads in the public source package, require the private
password, verify extracted ROM SHA against the matching build manifest, and run
the extracted real ROM in mGBA. Never put the password in public evidence/commits.
Preserve Mission012 stale/output and packaging negative tests.

## Historical retained Mission012/011 test plans

# Mission012 build foundation QA

Owner-reported Mission011 Windows/mGBA and physical-GBA acceptance: flicker fixed,
good audio, working score/holds/results/replay. This does not constitute agent
hardware testing or comprehensive certification. Mission012 Windows launcher
acceptance remains unchecked; see WINDOWS_PRIVATE_BUILD.md.

Run `bash tests/check.sh` (108 existing +19 new Python tests,8 sanitized C++
programs). Official clean builds use `python3 tools/build_profile.py public` and
`python3 tools/build_profile.py cream`. Both profiles must report the same full
source commit. Never use a stale root ROM left from low-level make.

Build a fresh exported source via release_common.source_snapshot/export_source,
then build both profiles independently. Place a unique fake payload in private/
before repeating public: require identical ROM hash, no marker in ROM/ZIP, and
no tracked/staged private/build files. Confirm public packaging rejects an actual
private result; damaged runtime/ROM rejects; invalid ZIP/missing input/failed
command yields failure, no new ROM and no latest-success pointer.

The complete selector label is checked against actual OAM and visible glyph
pixels by tests/build_identity_emulator.c (native libmgba0.10.1):

```bash
gcc -O2 -Wall -Wextra -Werror tests/build_identity_emulator.c -o /tmp/check-identity -lmgba
/tmp/check-identity PATH_TO_SYNTH_ROM "M012 / SYNTH"
/tmp/check-identity PATH_TO_PRIVATE_ROM "M012 / CREAM / LOCAL"
```

Full fresh results, exact commands/limits and source identities are in
MISSION_012_BUILD_FOUNDATION.md. Retained gameplay/graphics checks follow below;
M011-specific counts/times are historical evidence, not automatically attributed
to every future binary layout. For versioned builds use their matching ELF and
runtime header with the C harnesses, or copy a verified pair/header for the older
root-path wrappers. Do not mix profile files.

- [ ] Owner double-clicks Build-Cream-ROM.bat successfully on Windows11.
- [ ] Owner confirms printed M012 source/checksum and opens the newly built ROM.
- [ ] Owner checks full song, results/replay and flash-cartridge transfer.

## Retained gameplay and timing plan

### Mission011 reference checks

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
