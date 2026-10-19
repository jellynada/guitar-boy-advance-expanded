# Mission 009 — playable Easy sustains

Mission 009 starts at the owner-tested Mission 008 hotfix source commit
`71f0152c29d7008acd310808861643d5018e65a7`. Its delivered Cream ROM was on
`mission-008-hotfix-download` at `32e80153729d807aab9455f69221bd387a484e3b`.
The complete Mission 001–008 implementation chain is an ancestor of this source.
Work is on `mission-009-sustain-gameplay`; main is not merged.

## Playing

Choose **Imported Easy Test**. The selector now says **M009 HOLDS**.
Left, A and B are the three GBA lane buttons. A long colored line behind a note
means: hit its head, then keep that button held. You can hold A while playing B
or Left, including simultaneous A+B holds. The original four-lane demo is unchanged.

The head still earns Perfect 10 / Good 5 base points, increases combo once, and
uses the existing 1x–4x multiplier. A head miss or wrong new press resets combo
and mutes guitar; a successful head restores guitar. Sustain release does neither.

Each complete **250 milliseconds actually held** adds one bonus point multiplied
by the multiplier captured at that head's hit. Later combo changes do not change
that hold's rate. There are no fractional points or points past its real end.
Releasing early keeps previous points, pauses future bonuses immediately, and
does not change combo, accuracy, Full Combo, All Perfect or guitar volume.
A completed hold does not increase combo a second time.

Results preserve all previous statistics and instructions, adding **HOLDS DONE**,
**EARLY RELEASES** and **HOLD BONUS**. A/Start replays; B/Select returns to the
existing mode selector. Replay resets all hold states, bonuses and counters.

## Exact timing and edge policies

- All timing uses the same 16,777,216Hz sample-derived clock as note judgment.
  A quarter second is exactly 4,194,304 cycles; all counters are integers.
- A valid head hit starts its hold. Early hits cannot earn time before the
  scheduled head. Late hits earn only the actual time remaining before the
  chart's original end. An accepted head after a very short hold has already
  ended closes that hold with zero bonus. No bonus interval is rounded upward.
- A release has a **50ms grace period** for input bounce. Bonus time is credited through the observed release timestamp, so a release
  exactly at 250ms keeps its completed interval. It then pauses immediately;
  time between release and re-press observations earns no bonus.
  Returning within 50ms resumes the still-active hold; returning after the grace
  period cannot resume it. All new presses, including re-presses within grace, still use the unchanged
  head engine. An unmatched re-press can be WrongInput with its normal combo/
  guitar effect; grace does not synthesize or suppress head events.
- A release in the last 50ms may count as a completed hold, but earns no free
  remaining bonus time. That includes a fresh same-lane head within this end
  tolerance. Held input is piecewise constant until the next observed input
  transition; release timing has normal frame-poll resolution.
- Every new head still requires a fresh button press. For overlapping same-lane
  notes, a successful new head retires the older hold (early unless within its
  final 50ms). The new head may be a regular tap. No automatic presses are made.
  Different-lane holds remain independent; there can be three active holds.
- A wrong input or another head's miss does not cancel an already-held bonus
  rate. Those events keep their previous combo/guitar effects. Hold states
  never send audio events.
- Distinct states: non-hold, pending, active, completed, released early, missed
  onset. Missing a head never starts its hold. Duplicate hold-head events do
  not restart a completed/released hold or award points twice.
- Normal completion requires resolved head statistics **and** resolved holds.
  Audio EOF does not fabricate missing judgments. Invalid end data shows the
  existing visible DATA ERROR; audio faults retain AUDIO ERROR. Silent fallback
  waits for the latest head/hold end plus the existing late window and frame.

The hold controller has fixed storage: one state byte per head and three active
lane records, allocated in EWRAM. There is no per-frame allocation. Its ordinary
update inspects only three lanes. Head judgment/event order and the PCM mixer,
guitar gate, clock, audio rate and fade code are unchanged.

## Source preservation and compatibility

The actual Cream ZIP is still available locally. Its Easy track has **395 heads,
78 genuine sustains**, and PPQ 480. The existing classification is unchanged:
native length at least 160 ticks (PPQ/3), with positive duration. Short release
lengths remain taps. The source note records, raw MIDI lengths, adapted lanes
and complete guitar/backing PCM are preserved separately and compared against
Mission 008. No third-party content was substituted or truncated.

`Note` retains its established binary layout; active hold durations use the
existing parallel `imported_sustain_us` array. The adapter retains source MIDI
lengths in JSON. `tools/validate_holds.py` runs during every build, checking
parallel-array sizes, Easy lanes, sorted heads, supported duration/end bounds,
maximum 8192 heads, and hold ends against prepared audio EOF. Header hashes bind
prepared audio to the selected chart. Unsupported imported difficulties are
still rejected. Only Left/A/B controls are implemented here.

The synthetic fixture keeps 25 heads and now includes six genuine holds, regular
taps, long holds, simultaneous A+B, notes arriving during holds, and a same-lane
overlap. Completing every possible hold while hitting every head yields five
completed/one retired early (the overlapping B hold); head score remains 470.

## Drawing the tails

The existing perspective highway and note art are preserved. The tail endpoints
use the same camera transform, lane centers and audio-clock coordinates as the
head sprites. A tail is clipped to the existing one-second lookahead and the
fret line. An active tail remains visible after its head leaves the older 200ms
head window, shrinks toward its actual end, and disappears when completed or
released. Pending missed heads lose their tails when judged missed.

A narrow continuous lane-colored stripe is rasterized into 16x8 sprite strips.
The renderer examines at most 32 visible heads plus three older active holds.
Original heads retain OAM0–31 and their affine matrices. Tails use OAM32–127
and OBJ tiles192–383, below the original sprite-font tiles513+. OAM attribute3
(matrix storage) is preserved. The three-row BG0 HUD stays above tails; results
clear the sprite layer as before. Bounds checks prevent invalid pixel shifts.
The fixed 96-strip budget has a diagnostic overflow counter; tested charts
never overflow it. Highly unusual future charts still need measured acceptance
against this finite budget; import validation is not a blanket performance claim.

Known pre-existing visual issues include horizon/fog banding and occasional
sprite popping/scanline seams in the old perspective pipeline. This mission does
not redesign that pipeline. Native screenshots are included for owner review.

## Windows 11: public review ROM

Download and Extract All from the public Mission 009 review ZIP. In mGBA choose
File > Load ROM and open `Guitar-Boy-Advance-Mission-009-Synthetic.gba`.
Confirm **M009 HOLDS** and select Imported Easy Test. Configure GBA
Left/A/B under mGBA's keyboard settings. Download mGBA, if needed, from
https://mgba.io/downloads.html . This ROM contains original synthetic audio,
not Sunshine of Your Love.

## Windows 11: build your Cream ROM locally

The mission restricts public upload of the new Cream ROM without confirmation
of redistribution permissions. Earlier public builds are not that confirmation.
This environment has no private downloadable attachment/upload tool or connected
private file-transfer destination. GitHub API access returns Forbidden, so it
cannot provision a private repository or private release here. The actual Cream
ROM was built/tested locally, but a workspace path is not a Windows download.
The supported delivery path for this mission is the verified local build below.

### One-time setup

1. Install Ubuntu with WSL using Microsoft's guide:
   https://learn.microsoft.com/windows/wsl/install . The administrator PowerShell
   command is `wsl --install -d Ubuntu`; restart if Windows requests it, then open
   Ubuntu and complete its first-run setup.
2. Install Docker Desktop for Windows:
   https://docs.docker.com/desktop/setup/install/windows-install/ . Start Docker
   Desktop, use Linux containers, and enable Ubuntu in Settings > Resources >
   WSL Integration. Keep Docker Desktop running during the build.
3. In Ubuntu, run `sudo apt update && sudo apt install -y python3 ffmpeg` once.
   The password is your local Ubuntu password; do not send it to anyone.
4. Extract the public review ZIP. Open its `guitar-boy-advance-expanded` folder.
   Copy your existing Cream song ZIP into that folder and rename the copy
   `Cream.zip` (enable File name extensions in Windows Explorer to check its name).
5. Open Ubuntu in this source folder. For a typical download location:
   `cd "/mnt/c/Users/YOUR_WINDOWS_NAME/Downloads/mission009-review/guitar-boy-advance-expanded"`.
   Replace the username/folder with your actual extracted location.

### The two build commands

Copy and run these in Ubuntu, one at a time, from that source folder:

```bash
python3 tools/prepare_song.py Cream.zip --reactive --guitar-stem guitar --backing-stem rhythm --backing-stem song --output-dir imports/output/mission009
bash scripts/build-docker.sh "IMPORTED_HEADER=imports/output/mission009/imported_chart.hpp" "AUDIO_DIR=imports/output/mission009/audio"
```

Continue only if each command succeeds. The first validates/prepares your full
song; the second uses the pinned official devkitARM toolchain to build the ROM.
The preparer also prints legacy inspection-stage warnings about other
difficulties/bass and raw source sustains. Its initial "not playable" assessment
belongs to the old inspection stage; use the final Easy preparation and build
validation, not that initial assessment.
The first Docker run may download a large toolchain image. No programming or
source editing is needed. A failed build can leave an older output: only load
the output after both commands report success.

Your new file is **`guitar-boy-advance-expanded.gba`** in that source folder.
The selector's lower line should say **LOCAL / AUDIO** for Cream; the public
fixture says **SYNTH / AUDIO**. The local `Cream.zip` input is Git-ignored.
In mGBA choose File > Load ROM, open it, confirm M009 HOLDS and choose
Imported Easy Test. Load the ROM directly rather than restoring an old save state.
Both commands are exercised against the actual existing song ZIP during delivery
verification. They do not upload your song to GitHub.

See `MISSION_009_RESULTS.md` for exact evidence, artifact hashes, performance,
download verification and limits. No human Windows/hardware playtest is claimed.
