# Mission 008 — scoring, combos and results

Imported Easy Test now earns points, builds a combo and finishes with a results
screen. Its notes, controls and reactive guitar behavior stay as in Mission007.
Original Demo remains the existing699-note four-lane experience; it does not get
the new scoring/results flow in this mission.

## Download and play on Windows 11

1. Install mGBA from https://mgba.io/downloads.html .
2. Download and extract [mission008-review.zip](https://github.com/jellynada/guitar-boy-advance-expanded/raw/refs/heads/mission-008-download/downloads/mission008-review.zip).
3. In mGBA select File → Load ROM, then `guitar-boy-advance-mission-008.gba`.
4. Choose Imported Easy Test with Up/Down, then A or Start.
5. Map GBA Left / A / B to convenient computer keys. Release between notes.
6. Hit notes at the fret circles: S is score, C is current combo, X is multiplier.
7. Deliberately miss or press a wrong active button: combo/X reset and guitar
   mutes. Hit another note to restore guitar and start a new combo.
8. Let the entire recording finish to see results. A or Start replays;
   B or Select returns to mode selection. Start+Select also returns as before.

The public ROM uses original synthetic two-track audio with25notes. It does not
contain the Cream recording/chart. Original Demo still uses Left / Right / A / B.
No strum button, pause, save file, star rating or song-failure system is added.

## Exact rules

| Judgment | Base points | Combo |
| --- | ---: | --- |
| PerfectHit | 10 | Increase by1 |
| GoodHit | 5 | Increase by1 |
| Miss | 0 | Reset to0 |
| WrongInput | 0 | Reset to0 |

| Combo after this hit | Multiplier |
| --- | ---: |
| 0–9 | 1x |
| 10–19 | 2x |
| 20–29 | 3x |
| 30+ | 4x |

Combo increases **before** that note's points are calculated. Therefore the
10th/20th/30th consecutive Perfect is worth20/30/40, respectively. A Good at4x
is worth20. After a reset the next Perfect is worth10. Maximum combo/highest
multiplier remain remembered after mistakes. No extra bonus or sustain points.

The395-note all-Perfect reference is:

`9*10 +10*20 +10*30 +366*40 =15230`

The public25-note all-Perfect reference is470, with a25combo and highest3x.
An all-Good run scores half as much:private7615, public235. Both can be Full Combo.

## Accuracy and completion awards

Accuracy is `(Perfect+Good)/selected playable chart notes`, rounded to the nearest
hundredth of a percent using integer arithmetic.300/395 displays75.95%;0/395
is0.00%;395/395 is100.00%. Wrong inputs are listed separately and do not alter
the denominator or note accuracy. Empty test fixtures use0.00%, without division
by zero or completion awards.

- **Full Combo:** a completed, nonempty chart, every note Perfect/Good, no Miss
  and no WrongInput.
- **All Perfect:** Full Combo with every note Perfect and no Good.

100%note accuracy with wrong inputs qualifies for neither award. Awards are only
set after successful finalization, never for partial/interrupted sessions.

## Independent event consumer

`NoteScore<N>` in include/scoring.hpp consumes the existing GameplayEvent callback.
It owns score/combo/counts plus a fixed bitset with one bit per chart identity.
Duplicate or out-of-range chart identities cannot earn points twice or turn a hit
into a miss. WrongInput has no chart identity; each engine event counts once as a
wrong poll, including multiple unmatched buttons grouped by the existing engine.
The engine still decides what is a hit, chord member, miss or unmatched press.
Held/repeated presses and partial chords retain those established semantics.

No NoteJudgment windows or event emission code was changed. Expired misses are
emitted first, successful notes in lane order second, WrongInput last. Scoring
and guitar gating consume that same order. A missed older note followed by a hit
starts a new combo and restores guitar. A hit plus an extra wrong button earns
its valid points, then resets the combo and mutes guitar. Earlier earned points
are never subtracted. Maximum combo can include the hit before the final reset.

The audio callback is called separately before the scoring consumer. Score,
combo and multiplier never decide volume or playback position. The Mission007
PCM mixer,64sample fades, shared clock and stem preparation are unchanged.
Repeated-screen rendering cannot create points. No score allocations occur in
frame/interrupt/event paths. The bitset usesceil(N/8)bytes (50for395notes), with
fixed snapshots/counters in addition. Wrong counts and score use saturating32bit
addition. Supported8192-note charts cannot approach saturation; the score ceiling
is4,294,967,295rather than wrapping. HUD/result number fields fit10digits.

## HUD and graphics

Two8pixel rows at the top show score/combo and multiplier/judgment/guitar target.
Perfect/Good/Miss/Wrong feedback lasts18gameplay frames (about0.30s), replaced by
the next event. The existing guitar target label follows the same events; it does
not imply an in-progress4msfade is already complete.

The existing8x8font is reused, with no new art. Its HUD glyphs use unused BG0
character tiles128–223 and the first two rows of screenblock30, above the incoming
notes. BG1's existing black depth mask/blend remains in place while playing.
Results reuse the glyphs on BG1 with a black background and HBlank highway work
disabled. Replay/selection restores the normal layers, mask and blending. Score,
10digit values and temporary text have separate bounded fields. Results titles
use sanitized printable ASCII (header limit96characters, visible line28); long
or non-ASCII metadata can be clipped/replaced rather than corrupting VRAM.

## Safe song completion

Session state is Playing, Complete, AudioError or Inconsistent. Audio playback
and all selected chart notes must both be finished before Complete is entered.
A full chart resolved early still waits for the backing recording and padded
playback tail. A playback-end interrupt that arrives after the foreground snapshot defers
completion until the next snapshot catches up; results freeze the final clock.
Finalization also checks that scoring counts agree with the
judgment engine. The results screen shows title, score, accuracy, Perfect/Good/
Miss/Wrong counts, maximum combo, highest multiplier and eligible awards.

At completion, scoring and judgment stop accepting game input; the result stays
fixed. A or Start reuses the established fresh-mode initialization and resets
score, note states, held-key history, camera, both tracks and guitar gain. B or
Select returns to the selector. Merely viewing results cannot earn extra points.

An audio fault displays **AUDIO ERROR / SESSION INTERRUPTED** with partial
statistics and no completion awards. An ended recording with unresolved notes
or inconsistent statistics displays **DATA ERROR**, stops playback and never
claims a completed song. Both error states support replay or selection.

Labeled SILENT FALLBACK has a separate explicit endpoint:for a nonempty chart,
last note tick +85ms late window +one frame. Empty fixtures wait the2s pre-roll.
The last pending note is judged before completion is checked. Counts must still
be coherent; missing judgments cannot be fabricated into successful results.
Original Demo continues its old music-loop/chart behavior and has no automatic
results screen.

## Private Cream build on Windows 11

Use the full source folder inside the review ZIP. Install Ubuntu/WSL and Docker
Desktop with Ubuntu integration using the existing [setup guide](GBA_CHART_ADAPTATION.md#windows-11-chart-only-silent-fallback-without-editing-code).
Install host tools once in Ubuntu:

```bash
sudo apt update
sudo apt install python3 ffmpeg
```

Enter the source folder (replace YOURNAME/path with yours):

```bash
cd "/mnt/c/Users/YOURNAME/Downloads/mission008-review/guitar-boy-advance-expanded"
```

Place your existing Cream ZIP in `imports/incoming`. With Docker Desktop running,
execute these two commands in Ubuntu:

```bash
python3 tools/prepare_song.py "imports/incoming/Cream (WaveGroup) - Sunshine of Your Love (Neversoft).zip" --reactive --guitar-stem guitar --backing-stem rhythm --backing-stem song --output-dir imports/output/mission008
bash scripts/build-docker.sh "IMPORTED_HEADER=imports/output/mission008/imported_chart.hpp" "AUDIO_DIR=imports/output/mission008/audio"
```

Re-run preparation using Mission008 source so the bound header includes its result
title. Audio samples remain byte-identical to Mission007. Open the newly built
`guitar-boy-advance-expanded.gba` in mGBA and select Imported Easy Test. Only open
that output after both commands succeed; failures can leave an earlier ROM.

The private build and full traces remain local, outside public branches/artifacts.
This session has no working private artifact-export tool; a workspace path is not
a downloadable attachment. Exact saved paths and measured results are recorded
in [MISSION_008_RESULTS.md](MISSION_008_RESULTS.md). Do not publish private content
as part of the public synthetic bundle.

## Verification and limits

`bash tests/check.sh` covers rules, identities, real judgment event order, timing,
8192-note bounds, saturation, accuracy, empty charts, finalization, silence/fault
completion and prior importer/audio regressions. Automated mGBA runs inspect the
actual results tilemap as well as counters. They exercise full synthetic/private
songs, results/replay, selector controls, reactive captured sound, faults and
original699-note regressions. Exact performed checks are in the results document.

Owner feedback confirms Mission007 feel/sound; this mission does not claim human
playtesting or physical GBA validation of the new HUD/results. No saves, sustained
note scoring, new difficulties, audio format changes or full menus were added.
Recommended Mission009:owner HUD/results playtest, physical hardware validation,
then choose the next small design improvement based on that feedback.
