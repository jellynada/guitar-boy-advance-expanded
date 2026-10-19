# Mission 009 validation and delivery — 2026-10-19

## Verified base and scope

Base: owner-tested hotfix `71f0152c29d7008acd310808861643d5018e65a7`, whose
public download commit was `32e80153729d807aab9455f69221bd387a484e3b`.
Mission001–008 commits02e6bd8,79ea19a,747c3f7,4fa807c,1a6db8d,24ea658,
9baf71e,2e616e3 and the hotfix are ancestors. Source branch:
`mission-009-sustain-gameplay`. No main merge.

The original judgment engine, PCM playback, guitar gate, original sprite code,
Mode7 camera/affine code, original699-note chart, music and art are unchanged.
New hold logic is separate and uses the same sample-clock snapshots. Raw and
adapted Cream records compare equal to Mission008:395heads,78genuine sustains,
PPQ480,160tick threshold, no same-lane native sustain overlaps. Both full PCM
streams are byte-identical to Mission008. The source archive, recording and chart
were not published as Mission009 assets.

## Real Cream full-song acceptance

mGBA0.10.1+dfsg-1+deb12u1 library, actual supplied WaveGroup cover, all395Easy
heads, all78genuine hold lengths and the complete267.271912-second recording.
Each primary run executes16,400frames (~274seconds), covering2second lead-in,
all audio, normal EOF, visible results and navigation. Fresh replay is checked
for reset head/hold counters, advancing playback, and newly audible samples after
its lead-in. A/Start replay and B/Select menu return are exercised. Four more
rapid Original/Imported switches check the existing audio paths and epoch resets.

| Scenario | Total score | Holds complete | Early | Missed onset | Bonus |
| --- | ---: | ---: | ---: | ---: | ---: |
| sustain-perfect | 15815 | 78 | 0 | 0 | 585 |
| sustain-release | 15446 | 0 | 78 | 0 | 216 |
| perfect | 15230 | 0 | 78 | 0 | 0 |
| good | 7615 | 0 | 78 | 0 | 0 |
| miss | 0 | 0 | 0 | 78 | 0 |
| scoring | 2465 | 0 | 61 | 17 | 0 |
| wrong | 3860 | 0 | 78 | 0 | 0 |
| reactive | 2630 | 0 | 49 | 29 | 0 |
| returnmenu | 0 | 0 | 0 | 78 | 0 |
| returnselect | 0 | 0 | 0 | 78 | 0 |

Full-hold and early-release runs both retain395combo,4xhighest multiplier,
100.00% head accuracy, Full Combo and All Perfect. Early release sends **no**
guitar event: both traces contain exactly395Perfect head events and the guitar
remains audible. Normal head tapping still gives the15230-point reference.
The585/216bonuses are independently rebuilt from source durations, accepted-head
timestamps, captured multipliers and actual release-poll times by
`tests/analyze_sustains.py`. They are results of these scripted runs, not a promise
that every manually timed Perfect hit yields the identical bonus total.

The fixed250ms boundary test includes releasing exactly on the boundary: that
completed point is kept. A final50ms release tolerance still completes correctly
when the next foreground observation is delayed beyond the end. Re-presses after
expiry cannot reactivate a hold. Wrong-input events cannot change an active hold's
captured bonus rate. Source overlap tests require a fresh new head press.

## Visible display and navigation

The checks inspect actual final composed pixels, not only maps/counters:

- Live score/combo/multiplier digits at repeated stable gameplay frames.
- A quiet interval on the first genuine hold: unchanged head count and combo,
  score increases only by its250ms bonus, and the temporary judgment is gone.
  Both the real song and synthetic fixture pass this before/after screenshot test.
- Actual lane-colored tail pixels, original head-line positions at beginning,
  middle and end, and zero tail-budget overflow on every checked frame.
- Visible results heading, all old statistics/awards, all three new sustain rows,
  correct numerical values, and replay/menu instructions.
- Replay/menu state changes and fresh audio output, not only an internal flag.

The public fixture has25heads/sixholds; a full scripted run earns512points
(470head +42bonus), five completed holds and one early retirement caused by the
intentional same-lane overlap. A+B are held together for121frames in this run.
Three simultaneous hold lanes are also tested under sanitizers. Early-release
fixture runs preserve Full Combo/All Perfect despite releasing all six holds.
Public native240x160screenshots are in `screenshots/mission009/`; no synthetic
or edited replacement framebuffer is used as evidence for the real-song checks.

## Regression evidence

- All98Python tests and all C++ ASan/UBSan checks pass, including prior judgment,
  converters, MIDI/package import, exact sample clock, audio preparation, guitar
  gate/scoring and new hold/data validation tests.
- Original Demo: three36,000frame runs,699Perfect /699Miss /mixed, every head
  counted once, original sound and feedback present, no core crash.
- Seventeen synthetic scenarios pass: full holds, early releases, normalPerfect,
  Good, Miss, mixed, wrong, reactive, menu B/Select, replay Start, timer/DMA/sound/
  IRQ/underrun fault injection and inconsistent data. Errors show visible error
  headings/navigation with partial scores and no completion awards.
- The older fixed-mix complete recording and full silentPerfect/Miss paths pass
  completion, visible results, reset and menu regressions.
- Deliberately hiding BG0 or the results BG makes glyph checks fail as expected.
  These are explicit negative checks, not product test failures.
- Eight real reactive waveform models pass, covering full-hold/early-release,
  normalPerfect/Good/Miss, mixed, wrong and reactive hit/miss. Beginning/middle/
  end timing residuals stay below0.8ms; clipping and ordinary underruns are zero.
  Mute/recovery windows pass where the scenario requires them. Four public
  synthetic waveform models pass as well.

### Corrected measurement issues, without changing the audio engine

The legacy fixed-mix analyzer incorrectly required the foreground note snapshot
to be final in the very first row that an interrupt reported audio EOF. The
existing hotfix deliberately permits one catch-up snapshot. The analyzer now
requires frozen hardware consumption, at most one frame of initial foreground
lag, and exact final ticks afterward. An injected extra later clock change is
rejected by an explicit negative check.

That analyzer also used a single median capture epoch to claim sub-millisecond
drift across the entire song, mixing buffer phase variation into the measurement.
It now uses the nearest independently observed hardware/capture timestamp pair,
as the existing reactive analyzer already did, while retaining the global-epoch
residual in its report. The0.94correlation,3msabsolute error and0.2msdrift
limits are unchanged. The fixed-mix run passes with local residual drift recorded
in its report; the earlier global-epoch variation is retained rather than hidden.
No waveform quality threshold was relaxed and no PCM/mixer/clock code changed.

## ROMs, performance and reproducibility

- Private Cream: **9,171,164 bytes**, SHA-256 `e2e5a9740e7b75efbb70b0ba8e37a1fabdf41873932b4e50482290340336d214`.
- Public synthetic: **807,776 bytes**, SHA-256 `57ac5cb4201cd2f37e1124f27a89d05c115ff466cd9cea8e9d25748ea7a4e264`.

Maximum foreground interval across real-song scenarios: **170,176 CPUcycles**,
60.58% of a280896-cycle GBA frame. Measurements include overlapping
IRQ work and use a64-cycle profiling timer; they are emulator observations, not
physical hardware guarantees. Refill maxima stay comfortably below the16384-cycle
interval, with no ordinary underruns. Tail strips peak at11forCream and31for
the synthetic fixture, below96reserved slots; original heads retain32slots.

Linked IWRAM payload before stack:26,516bytes private /26,096bytes synthetic.
EWRAM:3,464 /3,096bytes respectively (plus linker padding). No per-frame heap
allocation. Both ROMs fit the standard32MiBcartridge bound.

Build compiler:devkitARM GCC16.1.0. Host conversion:FFmpeg7.1.5. The official
Docker toolchain digest is pinned in `scripts/build-docker.sh`. The exact two
commands in the Windows/WSL guide were executed from an isolated clean source
export with a real copy of the owner's ZIP named `Cream.zip`, producing a
byte-identical private ROM to the independently built/tested native result.
Ubuntu's FFmpeg package may differ on another machine; the byte-identical claim
here applies to the explicitly exercised environment. Windows GUI installation,
human keyboard playing/listening and physical GBA testing were not performed.

## Delivery and remaining limits

The public Mission009 review ZIP contains the syntheticROM, complete source,
public-native screenshots, public test logs, PR description and these instructions.
Publication uses a separate download branch. Download-back ZIP CRC/hash/source
verification is performed at handoff; its immutable link and exact revision are
reported with the final delivery. No main merge or public release is created.

The new Cream ROM remains local/private. No private upload/attachment capability
or connected private file destination is available. `gh api user` returns
Forbidden, so this environment cannot provision a private repository through
that API. The mission explicitly prohibits treating previous publicCream builds
as new redistribution permission. The actual supported owner delivery method is
the verified [Windows11local build](SUSTAIN_GAMEPLAY.md#windows-11-build-your-cream-rom-locally),
which produces `guitar-boy-advance-expanded.gba` from the owner's existing ZIP.
A cloud workspace path is not presented as a Windows download.

The owner still needs to judge sustain feel/visibility and listen on Windows11.
Existing horizon/fog bands and occasional sprite popping/scanline seams remain;
this mission does not redesign the perspective pipeline. Unusual future charts
need fresh visual/performance acceptance against finite sprite and memory budgets.
No imported Medium/Hard, new codec, song library, star power, health/failure or
new multiplier rules are implemented. Suggested next work: owner sustain
playtesting and focused graphics polish before multi-song planning.
